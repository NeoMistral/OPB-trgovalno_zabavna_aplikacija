import random
import poker_logic as Pl


# Function to call when user wants cards dealt
def deal_cards():
    global cards 
    global round
    round = 0
    cards = Pl.deal_cards()
    return cards

def increase_round():
    global round
    round += 1

def get_cards():
    global cards
    return cards
# This function converts cards to the right format for JS presentation
def convert_cards_for_js(cards):
    # {Player: [P1, P2], Dealer: [D1, D2], Community: [R1, R2, R3, R4, R5]}
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