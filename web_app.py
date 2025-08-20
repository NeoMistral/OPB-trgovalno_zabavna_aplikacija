from bottle import run, route, template, static_file, response, request, default_app
from beaker.middleware import SessionMiddleware
import poker_api
import poker_logic as Pl
import poker_index as Pi
import json
import funkcije
from poker_index import get_data
"""
In views there are templates,
in static we have css files and images
in poker_api there are poker functions for poker game


Game state is currently for memory, needs to be refactored, here we could use a database or 
session memory for just games.

Thats how game data in session looks like
game_data = {
    "round": 0,
    "player_cards": [],
    "dealer_cards": [], 
    "community_cards": [],
    "round_when_bet": None,
    "bet": 0,
    "blind": 1,
    "ante": 1,
    "won": 0,
    "winner": "TBD",
    "budget": 100,
}

"""
# Configure session storage
session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 3600,  # 1 hour
    'session.data_dir': './session_data',
    'session.auto': True
}

#base page
@route("/")
def home():
    return template("home")

#trading page
@route("/trading")
def trading():
    return template("trading")

#poker page
@route("/poker")
def poker():
    return template("poker")

@route('/api/deal', method='GET')
def api_deal():
    session = request.environ.get('beaker.session')
    # get dealt cards
    player, dealer, community = poker_api.deal_cards()
    session["game_data"]["round"] = 0
    session["game_data"]["player_cards"] = player
    session["game_data"]["dealer_cards"] = dealer
    session["game_data"]["community_cards"] = community
    cards = poker_api.convert_cards_for_js(player, dealer, community, 0) # round is always 0 here
    response.content_type = 'application/json'
    session.save()
    return json.dumps(cards)

@route('/api/check', metod='GET')
def api_check():
    # increse game round
    session = request.environ.get('beaker.session') 
    round = session["game_data"]["round"]
    round = poker_api.increase_round(round)
    session["game_data"]["round"] = round

    # get cards for display
    player = session["game_data"]["player_cards"]
    dealer = session["game_data"]["dealer_cards"]
    community = session["game_data"]["community_cards"]
    cards = poker_api.convert_cards_for_js(player, dealer, community, round)
    response.content_type = 'application/json'
    session.save()
    return json.dumps(cards)

# TODO: return game data after game end

@route('/api/bet', method='GET')
def api_bet():
    session = request.environ.get("beaker.session")
    round = session["game_data"]["round"]
    session["game_data"]["round_when_bet"] = round

    # set bet round
    game_data = session.get("game_data", {})
    bet = poker_api.set_bet_round(game_data)
    game_data["bet"] = bet
    game_data["round"] = 3

    # end game and calculate winnings
    winnings, winner, player_combo, dealer_combo = poker_api.end_game(game_data)
    game_data["won"] = winnings
    game_data["winner"] = winner
    game_data["budget"] += winnings

    session["game_data"] = game_data
    cards = poker_api.convert_cards_for_js(
        game_data["player_cards"],
        game_data["dealer_cards"],
        game_data["community_cards"],
        game_data["round"]
    )
    total_bet = bet + game_data.get("ante", 0) + game_data.get("blind", 0)
    get_data(total_bet, player_combo, dealer_combo)
    funkcije.update_portfolio_brez_cene(session["user_id"], game_data["stock"], game_data["budget"])#stock, change
    print("Cards", cards)
    response.content_type = 'application/json'
    session.save()
    return json.dumps(cards)

@route('/api/fold', method="GET")
def api_fold():
    session = request.environ.get("beaker.session")
    game_data, player_combo, dealer_combo = poker_api.end_game_by_fold(game_data=session["game_data"])
    session["game_data"] = game_data

    cards = poker_api.convert_cards_for_js(
        game_data["player_cards"],
        game_data["dealer_cards"],
        game_data["community_cards"],
        game_data["round"]
    )
    
    funkcije.update_portfolio_brez_cene(session["user_id"], game_data["stock"], game_data["budget"])#stock, change

    Pi.get_data(game_data["ante"] + game_data["blind"], player_combo, dealer_combo)
    
    response.content_type = 'application/json'
    session.save()
    return json.dumps(cards)

@route('/api/game-state', method='GET')
def api_game_state():
    # Try to get beaker session; may be None if middleware not applied
    session = request.environ.get('beaker.session')
    game_data = {}
    print('has beaker.session:', 'beaker.session' in request.environ)
    print('session type:', type(request.environ.get('beaker.session')))
    if session is not None:
        # session behaves like a dict
        game_data = session.get('game_data') or {}

    response.content_type = 'application/json'
    #print("Test",  game_data)
    return json.dumps(game_data)

# Route to serve static files (like CSS)
@route('/static/<filepath:path>')
def serve_static(filepath):
    return static_file(filepath, root='./static')

@route('/api/set_game_settings', method='POST')
def set_game_settings():
    session = request.environ.get("beaker.session")
    data = request.json
    print(data)

    # get and set game data
    game_data = session.get("game_data", {})
    game_data = poker_api.set_game_data(game_data, int(data.get('blind', 1)), int(data.get('ante', 1)))
    game_data["stock"] = data.get('stock')
    game_data["budget"] = calculate_budget_non_api(session['user_id'], data.get('stock'))
    game_data["bet"] = 0
    game_data["won"] = 0
    session["game_data"] = game_data
    response.content_type = 'application/json'
    session.save()
    return json.dumps({'status': 'success'})

@route('/login', method='POST')
def login():
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

# signing up user
@route('/signup', method='POST')
def signup():
    username = request.forms.get('username')
    password = request.forms.get('password')
    funkcije.registracija_uporabnika(username, password)
    funkcije.insert_user_stocks(funkcije.get_user_id(username))
    response.content_type = 'application/json'
    return json.dumps({'status': 'ok'})

@route('/api/sessionLogInCheck')
def api_session():
    session = request.environ.get('beaker.session')
    return {'logged_in': 'user_id' in session}

# get current stock prices
@route('/api/stocks')
def api_stocks():
    response.content_type = 'application/json'
    return json.dumps(funkcije.get_stock_prices())

# returns budget of user
@route('/api/budget', method='POST')
def calculate_budget():
    try:
        data = request.json
        symbol = data.get('stock') 
        session = request.environ.get('beaker.session')
        if 'user_id' not in session:
            response.status = 401
            return json.dumps({'error': 'Not logged in'})

        user_id = session['user_id']
        portfolio = funkcije.get_user_portfolio(user_id)  # Expecting list of {'symbol': ..., 'amount': ...}
        #print(portfolio)
        amount = 0
        for row in portfolio:
            if row.get("symbol") == symbol:
                amount = row.get("amount", 0)
                break

        print("amount", amount)
        response.content_type = 'application/json'
        return json.dumps({'budget': amount})

    except Exception as e:
        response.status = 500
        response.content_type = 'application/json'
        print(e)
        return json.dumps({'error': str(e)})

def calculate_budget_non_api(user_id, symbol):
    portfolio = funkcije.get_user_portfolio(user_id)  # Expecting list of {'symbol': ..., 'amount': ...}
    amount = 0
    for row in portfolio:
        if row.get("symbol") == symbol:
            amount = row.get("amount", 0)
            break

    return amount
    
# get user portfolio
@route('/api/portfolio')
def api_portfolio():
    session = request.environ.get('beaker.session')
    if 'user_id' not in session:
        response.status = 401
        return json.dumps({'error': 'Not logged in'})
    print(session['username'])
    user_id = session['user_id']
    data = {
        'username': session['username'],
        'balance': float(funkcije.get_user_balance(user_id)),
        'portfolio': funkcije.get_user_portfolio_all(user_id)
    }
    response.content_type = 'application/json'
    #print(data)
    return json.dumps(data)

@route('/api/buy', method='POST')
def api_buy():
    session = request.environ.get('beaker.session')
    if 'username' not in session:
        return {'status': 'error', 'error': 'Not logged in'}

    data = request.json
    if not funkcije.can_buy(session['user_id'], data['quantity'], data['price']):
        return {'status': 'error', 'error': 'Cannot buy this stock'}
    
    value = -data['price'] * data['quantity']
    funkcije.update_user_balance(session['user_id'], value)
    funkcije.update_portfolio(session['user_id'], data['symbol'], data['quantity'], data['price'])
    return {'status': 'ok'}

@route('/api/sell', method='POST')
def api_sell():
    session = request.environ.get('beaker.session')
    if 'username' not in session:
            return {'status': 'error', 'error': 'Not logged in'}

    data = request.json
    if not funkcije.can_sell(session['user_id'], data['symbol'], data['quantity']):
        return {'status': 'error', 'error': 'Cannot sell this stock'}

    value = data['price'] * data['quantity']
    funkcije.update_user_balance(session['user_id'], value)
    funkcije.update_portfolio(session['user_id'], data['symbol'], -data['quantity'], data['price'])
    return {'status': 'ok'}

app = SessionMiddleware(default_app(), session_opts)
run(hots="0.0.0.0", port=8080, app=app, debug=True, reloader=True)