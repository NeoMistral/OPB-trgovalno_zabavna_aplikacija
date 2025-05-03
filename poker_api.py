import random
import poker_logic as Pl
from game_state import game_data

# Function to call when user wants cards dealt
def deal_cards():
    cards = Pl.deal_cards()
    game_data["player_cards"] = cards[:2]
    game_data["dealer_cards"] = cards[2:4]
    game_data["community_cards"] = cards[4:]
    game_data["round"] = 0
    game_data["winnings"] = 0
    game_data["bet"] = 0

def increase_round():
    game_data["round"] += 1 if game_data["round"] < 3 else 0

# set how much is bet in each round
def set_bet_round():
    game_data["round_when_bet"] = game_data["round"]
    match game_data["round_when_bet"]:
        case 0:
            game_data["bet"] = 4 * game_data["ante"]
        case 1:
            game_data["bet"] = 2 * game_data["ante"]
        case 2:
            game_data["bet"] = 1 * game_data["ante"]

#end game when player has bet
def end_game():
    game_data["round"] = 3

    # calculate game result
    winner, winnings = Pl.calculate_game(game_data)
    game_data["won"] = winnings
    game_data["winner"] = winner
    game_data["budget"] += winnings

def end_game_by_fold():
    game_data["round"] = 3
    game_data["won"] = - (game_data["ante"] + game_data["blind"])
    game_data["budget"] += game_data["won"]
    game_data["winner"] = "dealer"

def set_game_data(blind, ante):
    print(blind, ante)
    game_data["blind"] = blind
    game_data["ante"] = ante
    game_data["bet"] = 0
    game_data["round"] = "None"
    game_data["round_when_bet"] = None
    game_data["won"] = 0

# This function converts cards to the right format for JS presentation
def convert_cards_for_js():
    # {Player: [P1, P2], Dealer: [D1, D2], Community: [R1, R2, R3, R4, R5]}
    cards = game_data["player_cards"] + game_data["dealer_cards"] + game_data["community_cards"]
    cards_csv = []

    hidden = []
    if game_data["round"] == 0:
        hidden = range(2, 9)
    elif game_data["round"] == 1:
        hidden = list(range(2, 4)) + list(range(7, 9))
    elif game_data["round"] == 2:
        hidden = range(2, 4)

    for card in cards:
        cards_csv.append(card["rank"] + card["suit"][0])
    
    for i in hidden:
        cards_csv[i] = "Hidden"

    cards_dict = {
        "player": cards_csv[:2],
        "dealer": cards_csv[2:4],
        "community": cards_csv[4:]
    }
    return cards_dict

