import random
import poker.poker_logic as Pl

# Function to call when user wants cards dealt
def deal_cards():
    """
    Deals cards for a new game round.

    Returns:
        tuple: (player_cards, dealer_cards, community_cards)
        - First 2 cards: player's hand
        - Next 2 cards: dealer's hand
        - Remaining cards: community cards
    """
    cards = Pl.deal_cards()
    return cards[:2], cards[2:4], cards[4:]


def increase_round(round):
    """
    Increments the game round counter (max 3).

    Args:
        round (int): current round number

    Returns:
        int: next round (capped at 3)
    """
    return round + 1 if round < 3 else round


def set_bet_round(game_data):
    """
    Calculates the bet size based on the round when betting occurred.

    Args:
        game_data (dict): current game state

    Returns:
        int/float: bet amount for the round
    """
    match game_data["round_when_bet"]:
        case 0:
            return 4 * game_data["ante"]   # Pre-flop (highest multiple)
        case 1:
            return 2 * game_data["ante"]   # Flop
        case 2:
            return 1 * game_data["ante"]   # Turn/River


def end_game(game_data):
    """
    Finalizes the game and determines the winner.

    Args:
        game_data (dict): current game state

    Returns:
        tuple: (winnings, winner, player_combo, dealer_combo)
        - winnings (int/float): net result for player
        - winner (str): 'player' or 'dealer'
        - player_combo (str): best poker hand of the player
        - dealer_combo (str): best poker hand of the dealer
    """
    winner, winnings, player_combo, dealer_combo = Pl.calculate_game(game_data)
    return winnings, winner, player_combo, dealer_combo


def end_game_by_fold(game_data):
    """
    Ends the game early when the player folds.

    Args:
        game_data (dict): current game state

    Returns:
        tuple: (updated game_data, player_combo, dealer_combo)
    """
    game_data["round"] = 3  # mark as ended
    # Player loses ante + blind
    game_data["won"] = - (game_data["ante"] + game_data["blind"])
    game_data["budget"] += game_data["won"]
    game_data["winner"] = "dealer"

    # Still calculate combos for logging/UI
    winner, winnings, player_combo, dealer_combo = Pl.calculate_game(game_data)
    return game_data, player_combo, dealer_combo


def set_game_data(game_data, blind, ante):
    """
    Initializes or resets game data for a new round.

    Args:
        game_data (dict): existing game state
        blind (int/float): blind value
        ante (int/float): ante value

    Returns:
        dict: updated game state
    """
    print(blind, ante)
    game_data["blind"] = blind
    game_data["ante"] = ante
    game_data["bet"] = 0
    game_data["round"] = "None"        # not started yet
    game_data["round_when_bet"] = None # reset betting round
    game_data["won"] = 0
    return game_data


def convert_cards_for_js(player, dealer, community, round):
    """
    Converts card objects into a JavaScript-friendly format
    (strings like "AS" for Ace of Spades, with some hidden depending on round).

    Args:
        player (list): player's cards (2)
        dealer (list): dealer's cards (2)
        community (list): community cards (5)
        round (int): current round number (0=preflop, 1=flop, 2=turn, 3=river)

    Returns:
        dict: {
            "player": [...],   # 2 player cards
            "dealer": [...],   # 2 dealer cards (partially hidden)
            "community": [...] # 5 community cards (partially hidden)
        }
    """
    # Flatten all cards
    cards = player + dealer + community
    cards_csv = []

    # Define which indices should be hidden depending on round
    hidden = []
    if round == 0:   # preflop: hide all dealer + community
        hidden = range(2, 9)
    elif round == 1: # flop: hide dealer + last 2 community
        hidden = list(range(2, 4)) + list(range(7, 9))
    elif round == 2: # turn: hide dealer only
        hidden = range(2, 4)

    # Convert each card to "RankSuit" (e.g., "AS", "10H")
    for card in cards:
        cards_csv.append(card["rank"] + card["suit"][0])

    # Mask hidden cards
    for i in hidden:
        cards_csv[i] = "Hidden"

    # Split back into player, dealer, and community
    cards_dict = {
        "player": cards_csv[:2],
        "dealer": cards_csv[2:4],
        "community": cards_csv[4:]
    }
    return cards_dict
