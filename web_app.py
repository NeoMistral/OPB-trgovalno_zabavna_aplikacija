from bottle import run, route, template, static_file, response
import poker_api
import json
"""
In views there are templates,
in static we have css files and images
in poker_api there are poker functions for poker game
"""


#base page
@route("/")
def home():
    return template("home")


#poker page
@route("/poker")
def poker():
    return template("poker")

@route('/api/deal', method='GET')
def api_cards():
    cards = poker_api.deal_cards()
    cards = poker_api.convert_cards_for_js(cards)
    poker_api.increase_round()
    response.content_type = 'application/json'
    return json.dumps(cards)

@route('/api/check', metod='GET')
def api_check():
    cards = poker_api.get_cards()
    cards = poker_api.convert_cards_for_js(cards)
    poker_api.increase_round()
    response.content_type = 'application/json'
    return json.dumps(cards)



# Route to serve static files (like CSS)
@route('/static/<filepath:path>')
def serve_static(filepath):
    return static_file(filepath, root='./static')

run(debug=True, reloader=True)