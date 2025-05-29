from bottle import run, route, template, static_file, response, request
import poker_api
import json
"""
In views there are templates,
in static we have css files and images
in poker_api there are poker functions for poker game


Game state is currently for memory, needs to be refactored, here we could use a database or 
session memory for just games.
"""


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
    poker_api.deal_cards()
    cards = poker_api.convert_cards_for_js()
    response.content_type = 'application/json'
    return json.dumps(cards)

@route('/api/check', metod='GET')
def api_check():
    poker_api.increase_round()
    cards = poker_api.convert_cards_for_js()
    response.content_type = 'application/json'
    return json.dumps(cards)

@route('/api/bet', method='GET')
def api_bet():
    poker_api.set_bet_round()
    poker_api.end_game()
    cards = poker_api.convert_cards_for_js()
    response.content_type = 'application/json'
    return json.dumps(cards)

@route('/api/fold', method="GET")
def api_fold():
    poker_api.end_game_by_fold()
    cards = poker_api.convert_cards_for_js()
    response.content_type = 'application/json'
    return json.dumps(cards)

@route('/api/game-state', method='GET')
def api_game_state():
    response.content_type = 'application/json'
    return json.dumps(poker_api.game_data)

# Route to serve static files (like CSS)
@route('/static/<filepath:path>')
def serve_static(filepath):
    return static_file(filepath, root='./static')

@route('/api/set_game_settings', method='POST')
def set_game_settings():
    data = request.json
    print(data)
    poker_api.set_game_data(int(data.get('blind', 1)), int(data.get('ante', 1)))
    response.content_type = 'application/json'
    return json.dumps({'status': 'success'})

#temporary
def get_stock_prices():
    return [
        {'symbol': 'AAPL', 'price': 192.35},
        {'symbol': 'GOOGL', 'price': 2841.45},
        {'symbol': 'AMZN', 'price': 3467.42}
    ]
# API route to return stock prices as JSON
@route('/api/stocks')
def api_stocks():
    response.content_type = 'application/json'
    return json.dumps(get_stock_prices())



run(debug=True, reloader=True)