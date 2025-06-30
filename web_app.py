from bottle import run, route, template, static_file, response, request, default_app
from beaker.middleware import SessionMiddleware
import poker_api
import json
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

TODO: selling and buying, logging in
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
    balance = calculate_budget()
    session["game_data"] = {
        "round": 0,
        "player_cards": player,
        "dealer_cards": dealer,
        "community_cards": community,
        "bet": 0,
        "won": 0,
        "winner": "TBD",
        "budget": balance,
        "blind": 1, # default blind
        "ante": 1, # default ante
        "round_when_bet": None
    }
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

@route('/api/bet', method='GET')
def api_bet():
    # set bet round
    session = request.environ.get("beaker.session")
    round = session["game_data"]["round"]
    session["game_data"]["round_when_bet"] = round

    # get how much to bet and round to 3
    game_data = session.get("game_data", {})
    bet = poker_api.set_bet_round(game_data)
    session["game_data"]["bet"] = bet
    session["game_data"]["round"] = 3
    game_data["bet"] = bet
    game_data["round"] = 3

    # end game and calculate winning and winner
    winnings, winner = poker_api.end_game(game_data)
    session["game_data"]["won"] = winnings
    session["game_data"]["winner"] = winner
    session["game_data"]["budget"] += winnings

    # get cards for display
    player = session["game_data"]["player_cards"]
    dealer = session["game_data"]["dealer_cards"]
    community = session["game_data"]["community_cards"]
    cards = poker_api.convert_cards_for_js(player, dealer, community, round)
    response.content_type = 'application/json'
    session.save()
    return json.dumps(cards)

@route('/api/fold', method="GET")
def api_fold():
    session = request.environ.get("beaker.session")
    game_data = poker_api.end_game_by_fold(game_data=session["game_data"])
    session["game_data"] = game_data

    # get cards for display
    player = session["game_data"]["player_cards"]
    dealer = session["game_data"]["dealer_cards"]
    community = session["game_data"]["community_cards"]
    cards = poker_api.convert_cards_for_js(player, dealer, community, round)
    response.content_type = 'application/json'
    session.save()
    return json.dumps(cards)

@route('/api/game-state', method='GET')
def api_game_state():
    session = request.environ.get('beaker.session')
    response.content_type = 'application/json'
    return json.dumps(session.get('game_data', {}))

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
    session["game_data"] = game_data
    response.content_type = 'application/json'
    session.save()
    return json.dumps({'status': 'success'})

# - BAZE (false če ne obstaja)
def get_user(username, password):
    pass

@route('/login', method='POST')
def login():
    session = request.environ.get('beaker.session')
    username = request.forms.get('username')
    password = request.forms.get('password')

    # Dummy auth check (replace with DB lookup)
    if username == 'alice' and password == 'secret':
        session['user_id'] = 1
        session['username'] = username
        session.save()
        response.content_type = 'application/json'
        return json.dumps({'status': 'ok'})
    else:
        response.status = 401
        response.content_type = 'application/json'
        return json.dumps({'status': 'fail', 'error': 'Invalid credentials'})
    
#temporary - BAZE
def get_stock_prices():
    return [
        {'symbol': 'AAPL', 'price': 192.35},
        {'symbol': 'GOOGL', 'price': 2841.45},
        {'symbol': 'AMZN', 'price': 3467.42}
    ]

# Compute budget based on selected stock BAZE - update number of owned stocks
@route('/api/budget', method='POST')
def calculate_budget():
    try:
        data = request.json
        symbol = data.get('stock')  # 'B', for example
        print(symbol)
        session = request.environ.get('beaker.session')
        if 'user_id' not in session:
            response.status = 401
            return json.dumps({'error': 'Not logged in'})

        user_id = session['user_id']
        portfolio = get_user_portfolio(user_id)  # Expecting list of {'symbol': ..., 'amount': ...}
        print(portfolio)
        amount = 0
        for row in portfolio:
            if row.get("symbol") == symbol:
                amount = row.get("amount", 0)
                break

        budget = amount  # Replace with real logic

        response.content_type = 'application/json'
        return json.dumps({'budget': budget})

    except Exception as e:
        response.status = 500
        response.content_type = 'application/json'
        print(e)
        return json.dumps({'error': str(e)})

# API route to return stock prices as JSON
@route('/api/stocks')
def api_stocks():
    response.content_type = 'application/json'
    return json.dumps(get_stock_prices())


#get user balance - BAZE 
def get_user_balance(user_id):
    return 1234

#get user portfolio - BAZE
def get_user_portfolio(user_id):
    return [{"symbol": "O", "amount": 0},
            {"symbol": "B", "amount": 1}]
# get user data
def get_user_data():
    session = request.environ.get('beaker.session')
    if 'user_id' not in session:
        response.status = 401
        return {'error': 'Not logged in'}

    user_id = session['user_id']
    username = session.get('username')  # assuming you saved it during login
    balance = get_user_balance(user_id)  # your function to get balance
    portfolio = get_user_portfolio(user_id)  # your function to get portfolio

    response.content_type = 'application/json'
    return {
        'username': username,
        'balance': balance,
        'portfolio': portfolio
    }

@route('/api/portfolio')
def api_portfolio():
    response.content_type = 'application/json'
    return json.dumps(get_user_data())

@route('/api/sessionLogInCheck')
def api_session():
    session = request.environ.get('beaker.session')
    return {'logged_in': 'user_id' in session}

@route('/signup', method='POST')
def signup():
    username = request.forms.get('username')
    password = request.forms.get('password')
    # Your user creation logic here
    print(username, password)

    response.content_type = 'application/json'
    return json.dumps({'status': 'ok'})

@route('/api/buy', method='POST')
def api_buy():
    session = request.environ.get('beaker.session')
    user = session['username']
    
    if not user:
        return {'status': 'error', 'error': 'Not logged in'}

    data = request.json
    symbol = data.get('symbol')
    quantity = data.get('quantity')
    price = data.get('price')

    if not can_buy(user, symbol, quantity, price):
        return {'status': 'error', 'error': 'Cannot buy this stock'}

    # Update balance BAZE

    # Update portfolio BAZE
    return {'status': 'ok'}

@route('/api/sell', method='POST')
def api_sell():
    session = request.environ.get('beaker.session')
    user = session['username']

    if not user:
        return {'status': 'error', 'error': 'Not logged in'}

    data = request.json
    symbol = data.get('symbol')
    quantity = data.get('quantity')
    price = data.get('price')

    if not can_sell(user, symbol, quantity):
        return {'status': 'error', 'error': 'Cannot sell this stock'}

    # Update balance

    # Update portfolio
    
    return {'status': 'ok'}

# BAZE
def can_buy(user, symbol, quantity, price):
    print(user)
    return True

def can_sell(user, symbol, quantity):
    return True

app = SessionMiddleware(default_app(), session_opts)
run(hots="0.0.0.0", port=8080, app=app, debug=True, reloader=True)