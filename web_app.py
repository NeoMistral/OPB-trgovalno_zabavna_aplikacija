from bottle import run, route, template, static_file, response, request, default_app
from beaker.middleware import SessionMiddleware
import poker.poker_api as poker_api
import poker.poker_index as Pi
import json
import baze.funkcije as funkcije

# Configure session storage
session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 3600,  # 1 hour
    'session.data_dir': './session_data',
    'session.auto': True
}

# -------------------------
# Templates / UI routes
# -------------------------

@route("/")
def home():
    """Render the home page template."""
    return template("home")


@route("/trading")
def trading():
    """Render the trading page template."""
    return template("trading")


@route("/poker")
def poker():
    """Render the poker page template."""
    return template("poker")


# -------------------------
# Poker API routes
# -------------------------

@route('/api/deal', method='GET')
def api_deal():
    """
    Deal initial poker cards.
    Stores them in session and returns masked card data for the frontend.
    """
    session = request.environ.get('beaker.session')
    player, dealer, community = poker_api.deal_cards()
    session["game_data"]["round"] = 0
    session["game_data"]["player_cards"] = player
    session["game_data"]["dealer_cards"] = dealer
    session["game_data"]["community_cards"] = community
    cards = poker_api.convert_cards_for_js(player, dealer, community, 0)
    response.content_type = 'application/json'
    session.save()
    return json.dumps(cards)


@route('/api/check', metod='GET')
def api_check():
    """
    Advance the poker round (check action).
    Reveals additional cards according to round.
    """
    session = request.environ.get('beaker.session')
    round = session["game_data"]["round"]
    round = poker_api.increase_round(round)
    session["game_data"]["round"] = round

    player = session["game_data"]["player_cards"]
    dealer = session["game_data"]["dealer_cards"]
    community = session["game_data"]["community_cards"]
    cards = poker_api.convert_cards_for_js(player, dealer, community, round)
    response.content_type = 'application/json'
    session.save()
    return json.dumps(cards)


@route('/api/bet', method='GET')
def api_bet():
    """
    Place a bet for current round.
    Calculates winnings, updates session state and portfolio, returns card info.
    """
    session = request.environ.get("beaker.session")
    round = session["game_data"]["round"]
    session["game_data"]["round_when_bet"] = round

    game_data = session.get("game_data", {})
    bet = poker_api.set_bet_round(game_data)
    game_data["bet"] = bet
    game_data["round"] = 3

    winnings, winner, player_combo, dealer_combo = poker_api.end_game(game_data)
    game_data["won"] = winnings
    game_data["winner"] = winner
    game_data["budget"] += winnings

    session["game_data"] = game_data
    cards = poker_api.convert_cards_for_js(
        game_data["player_cards"], game_data["dealer_cards"], game_data["community_cards"], game_data["round"]
    )
    total_bet = bet + game_data.get("ante", 0) + game_data.get("blind", 0)
    amount = Pi.izracunaj_bet(game_data["stock"], total_bet)
    Pi.get_data(amount, player_combo, dealer_combo)
    funkcije.update_portfolio_brez_cene(session["user_id"], game_data["stock"], game_data["budget"])
    response.content_type = 'application/json'
    session.save()
    return json.dumps(cards)


@route('/api/fold', method="GET")
def api_fold():
    """
    Handle a fold action by the player.
    Ends the game, updates portfolio and returns revealed cards.
    """
    session = request.environ.get("beaker.session")
    game_data, player_combo, dealer_combo = poker_api.end_game_by_fold(session["game_data"])
    session["game_data"] = game_data
    game_data["round"] = 3
    cards = poker_api.convert_cards_for_js(
        game_data["player_cards"], game_data["dealer_cards"], game_data["community_cards"], game_data["round"]
    )

    funkcije.update_portfolio_brez_cene(session["user_id"], game_data["stock"], game_data["budget"])
    amount = Pi.izracunaj_bet(game_data["stock"], game_data["ante"] + game_data["blind"])
    Pi.get_data(amount, player_combo, dealer_combo)

    response.content_type = 'application/json'
    session.save()
    return json.dumps(cards)


@route('/api/game-state', method='GET')
def api_game_state():
    """
    Returns current poker game state stored in session.
    """
    session = request.environ.get('beaker.session')
    game_data = {}
    if session is not None:
        game_data = session.get('game_data') or {}
    response.content_type = 'application/json'
    return json.dumps(game_data)


@route('/api/set_game_settings', method='POST')
def set_game_settings():
    """
    Initializes poker game settings (blind, ante, stock) for the session.
    """
    session = request.environ.get("beaker.session")
    data = request.json

    game_data = session.get("game_data", {})
    game_data = poker_api.set_game_data(game_data, int(data.get('blind', 1)), int(data.get('ante', 1)))
    game_data["stock"] = data.get('stock')
    game_data["budget"] = calculate_budget_non_api(session['user_id'], data.get('stock'))
    game_data["bet"] = 0
    game_data["won"] = 0
    game_data["round"] = -1
    session["game_data"] = game_data
    response.content_type = 'application/json'
    session.save()
    return json.dumps({'status': 'success'})


@route('/api/canBuy', method=['GET', 'POST'])
def can_buy():
    """
    Check if the player has enough budget to continue betting.
    If not, adjusts round state accordingly.
    """
    session = request.environ.get("beaker.session")
    if session is None:
        response.status = 500
        response.content_type = 'application/json'
        return json.dumps({'error': 'Session not available'})

    game_data = session.get("game_data") or {}
    round_ = game_data.get("round", 0)
    blind = game_data.get("blind")
    ante = game_data.get("ante")
    budget = game_data.get("budget")

    multiplier = 4
    required = (blind + ante) * multiplier
    can = budget >= required

    if not can:
        game_data["round"] = -2
        session["game_data"] = game_data
        session.save()

    response.content_type = 'application/json'
    return json.dumps({'can': can})


# -------------------------
# Authentication routes
# -------------------------

@route('/login', method='POST')
def login():
    """
    Handle user login. Checks credentials and stores user_id + username in session.
    """
    session = request.environ.get('beaker.session')
    username = request.forms.get('username')
    password = request.forms.get('password')

    if funkcije.check_if_user_exists(username, password):
        user_id = funkcije.get_user_id(username)
        session['user_id'] = user_id
        session['username'] = username
        session.save()
        response.content_type = 'application/json'
        return json.dumps({'status': 'ok'})
    else:
        response.status = 401
        response.content_type = 'application/json'
        return json.dumps({'status': 'fail', 'error': 'Invalid credentials'})


@route('/signup', method='POST')
def signup():
    """
    Handle new user registration.
    Returns error if username already exists.
    """
    username = request.forms.get('username')
    password = request.forms.get('password')
    isOk = funkcije.registracija_uporabnika(username, password)
    if isOk:
        funkcije.insert_user_stocks(funkcije.get_user_id(username))
    response.content_type = 'application/json'
    error = "Username already exists" if not isOk else "ok"
    return json.dumps({'error': error})


@route('/api/sessionLogInCheck')
def api_session():
    """
    Check if user is logged in (session contains user_id).
    """
    session = request.environ.get('beaker.session')
    return {'logged_in': 'user_id' in session}


# -------------------------
# Trading routes
# -------------------------

@route('/api/stocks')
def api_stocks():
    """
    Returns current stock prices from the database.
    """
    response.content_type = 'application/json'
    return json.dumps(funkcije.get_stock_prices())


@route('/api/budget', method='POST')
def calculate_budget():
    """
    Returns the number of units of a given stock the user currently owns.
    """
    try:
        data = request.json
        symbol = data.get('stock')
        session = request.environ.get('beaker.session')
        if 'user_id' not in session:
            response.status = 401
            return json.dumps({'error': 'Not logged in'})

        user_id = session['user_id']
        portfolio = funkcije.get_user_portfolio(user_id)
        amount = 0
        for row in portfolio:
            if row.get("symbol") == symbol:
                amount = row.get("amount", 0)
                break

        response.content_type = 'application/json'
        return json.dumps({'budget': amount})

    except Exception as e:
        response.status = 500
        response.content_type = 'application/json'
        return json.dumps({'error': str(e)})


def calculate_budget_non_api(user_id, symbol):
    """
    Helper: same as /api/budget but without HTTP wrapping.
    """
    portfolio = funkcije.get_user_portfolio(user_id)
    amount = 0
    for row in portfolio:
        if row.get("symbol") == symbol:
            amount = row.get("amount", 0)
            break
    return amount


@route('/api/portfolio')
def api_portfolio():
    """
    Returns full portfolio and balance of logged-in user.
    """
    session = request.environ.get('beaker.session')
    if 'user_id' not in session:
        response.status = 401
        return json.dumps({'error': 'Not logged in'})

    user_id = session['user_id']
    data = {
        'username': session['username'],
        'balance': float(funkcije.get_user_balance(user_id)),
        'portfolio': funkcije.get_user_portfolio_all(user_id)
    }
    response.content_type = 'application/json'
    return json.dumps(data)


@route('/api/buy', method='POST')
def api_buy():
    """
    Process a stock purchase request.
    Updates balance, portfolio, and logs transaction.
    """
    session = request.environ.get('beaker.session')
    if 'username' not in session:
        return {'status': 'error', 'error': 'Not logged in'}

    data = request.json
    if not funkcije.can_buy(session['user_id'], data['quantity'], data['price']):
        return {'status': 'error', 'error': 'Cannot buy this stock'}

    value = -data['price'] * data['quantity']
    funkcije.update_user_balance(session['user_id'], value)
    funkcije.update_portfolio(session['user_id'], data['symbol'], data['quantity'], data['price'])
    funkcije.add_transaction(session['user_id'], data['symbol'], data['quantity'], data['price'] * data['quantity'])
    return {'status': 'ok'}


@route('/api/sell', method='POST')
def api_sell():
    """
    Process a stock sale request.
    Updates balance, portfolio, and logs transaction.
    """
    session = request.environ.get('beaker.session')
    if 'username' not in session:
        return {'status': 'error', 'error': 'Not logged in'}

    data = request.json
    if not funkcije.can_sell(session['user_id'], data['symbol'], data['quantity']):
        return {'status': 'error', 'error': 'Cannot sell this stock'}

    value = data['price'] * data['quantity']
    funkcije.update_user_balance(session['user_id'], value)
    funkcije.update_portfolio(session['user_id'], data['symbol'], -data['quantity'], data['price'])
    funkcije.add_transaction(session['user_id'], data['symbol'], -data['quantity'], data['price'] * data['quantity'])
    return {'status': 'ok'}


# -------------------------
# Static file route
# -------------------------

@route('/static/<filepath:path>')
def serve_static(filepath):
    """Serve static files (CSS, JS, images)."""
    return static_file(filepath, root='./static')


# -------------------------
# App entrypoint
# -------------------------

app = SessionMiddleware(default_app(), session_opts)
run(host="0.0.0.0", port=8080, app=app, debug=True, reloader=True)
