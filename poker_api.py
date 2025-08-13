import random
import poker_logic as Pl

# Function to call when user wants cards dealt
def deal_cards():
    cards = Pl.deal_cards()
    return cards[:2], cards[2:4], cards[4:]

def increase_round(round):
    return round + 1 if round < 3 else round

# set how much is bet in each round
def set_bet_round(game_data):
    match game_data["round_when_bet"]:
        case 0:
            return 4 * game_data["ante"]
        case 1:
            return 2 * game_data["ante"]
        case 2:
            return 1 * game_data["ante"]

#end game when player has bet
def end_game(game_data):

    # calculate game result
    winner, winnings, player_combo, dealer_combo = Pl.calculate_game(game_data)
    return winnings, winner, player_combo, dealer_combo

def end_game_by_fold(game_data):
    game_data["round"] = 3
    game_data["won"] = - (game_data["ante"] + game_data["blind"])
    game_data["budget"] += game_data["won"]
    game_data["winner"] = "dealer"
    winner, winnings, player_combo, dealer_combo = Pl.calculate_game(game_data)
    return game_data, player_combo, dealer_combo

def set_game_data(game_data, blind, ante):
    print(blind, ante)
    game_data["blind"] = blind
    game_data["ante"] = ante
    game_data["bet"] = 0
    game_data["round"] = "None"
    game_data["round_when_bet"] = None
    game_data["won"] = 0
    return game_data

# This function converts cards to the right format for JS presentation
def convert_cards_for_js(player, dealer, community, round):
    # {Player: [P1, P2], Dealer: [D1, D2], Community: [R1, R2, R3, R4, R5]}
    cards = player + dealer + community
    cards_csv = []

    hidden = []
    if round == 0:
        hidden = range(2, 9)
    elif round == 1:
        hidden = list(range(2, 4)) + list(range(7, 9))
    elif round == 2:
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

