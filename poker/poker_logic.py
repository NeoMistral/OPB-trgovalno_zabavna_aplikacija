import random
from collections import Counter

# define card set
suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
rank_values = {rank: i for i, rank in enumerate(ranks, start=2)}

deck = [{'rank': rank, 'suit': suit} for suit in suits for rank in ranks]

budget = 1000
combinations = ["High Card", "One Pair", "Two Pair", "Three of a Kind", "Four of a Kind", 
                "Full House", "Straight", "Flush", "Straight Flush", "Royal Flush"]
combinations_values = {combination: i for i, combination in enumerate(combinations, start=1)}

# remove a card from the deck and return it "deal a card"
def deal_card(deck):
    """
    Removes and returns one random card from the given deck.

    Args:
        deck (list): list of cards

    Returns:
        dict: card object removed from deck
    """
    return deck.pop(random.randint(0, len(deck) - 1))


# function for determining whether a player should bet before flop
def should_raise_pre_flop(card1, card2):
    """
    Decides whether a player should raise pre-flop based on two hole cards.

    Args:
        card1 (dict): first card { 'rank': str, 'suit': str }
        card2 (dict): second card { 'rank': str, 'suit': str }

    Returns:
        int: amount to bet (4 for raise, 0 for no raise)
    """
    higher, lower = sorted([card1, card2], key=lambda c: ranks.index(c['rank']), reverse=True)

    if higher['rank'] == lower['rank'] and ranks.index(higher['rank']) >= ranks.index('3'):
        return 4

    decision_table = {
        ('A', '2'): 'Y', ('A', '3'): 'Y', ('A', '4'): 'Y', ('A', '5'): 'Y', ('A', '6'): 'Y', ('A', '7'): 'Y', ('A', '8'): 'Y', ('A', '9'): 'Y', ('A', '10'): 'Y', ('A', 'J'): 'Y', ('A', 'Q'): 'Y', ('A', 'K'): 'Y',
        ('K', '2'): 'S', ('K', '3'): 'S', ('K', '4'): 'S', ('K', '5'): 'Y', ('K', '6'): 'Y', ('K', '7'): 'Y', ('K', '8'): 'S', ('K', '9'): 'S', ('K', '10'): 'Y', ('K', 'J'): 'Y', ('K', 'Q'): 'Y',
        ('Q', '6'): 'S', ('Q', '7'): 'S', ('Q', '8'): 'Y', ('Q', '9'): 'Y', ('Q', '10'): 'Y', ('Q', 'J'): 'Y',
        ('J', '8'): 'S', ('J', '9'): 'S', ('J', '10'): 'Y'}
    
    decision = decision_table.get((higher['rank'], lower['rank']), 'N')
    return 4 if decision == 'Y' else 4 if decision == 'S' and higher['suit'] == lower['suit'] else 0


# function that returns the best hand from available cards
def get_best_hand(cards):
    """
    Evaluates a list of cards and determines the strongest poker hand.

    Args:
        cards (list): list of card dicts

    Returns:
        str: best hand name (e.g., "Straight", "Flush", "High Card")
    """
    rank_counts = Counter(card['rank'] for card in cards)
    suit_counts = Counter(card['suit'] for card in cards)
    numeric_ranks = sorted([rank_values[card['rank']] for card in cards], reverse=True)
    unique_numeric_ranks = sorted(list(set(numeric_ranks)), reverse=True)
    
    # Check flush possibilities
    most_common_suit, highest_suit_count = suit_counts.most_common(1)[0]
    if highest_suit_count >= 5:
        flush_cards = [card for card in cards if card['suit'] == most_common_suit]
        flush_ranks = sorted([rank_values[card['rank']] for card in flush_cards], reverse=True)
        flush_rank_strings = [card['rank'] for card in flush_cards]
        
        # Check royal flush
        if {'10', 'J', 'Q', 'K', 'A'}.issubset(flush_rank_strings):
            return "Royal Flush"
            
        # Check straight flush (including Ace-low)
        for i in range(len(flush_ranks) - 4):
            if flush_ranks[i] - flush_ranks[i+4] == 4:
                return "Straight Flush"
        # Special case for Ace-low straight flush (5-4-3-2-A)
        if set([14, 5, 4, 3, 2]).issubset(flush_ranks):
            return "Straight Flush"
    
    # Check four of a kind
    if 4 in rank_counts.values():
        return "Four of a Kind"
    
    # Check full house (three + two, or two three-of-a-kinds)
    if (3 in rank_counts.values() and 2 in rank_counts.values()) or list(rank_counts.values()).count(3) >= 2:
        return "Full House"
    
    # Check flush
    if highest_suit_count >= 5:
        return "Flush"
    
    # Check straight (including Ace-low)
    if len(unique_numeric_ranks) >= 5:
        for i in range(len(unique_numeric_ranks) - 4):
            if unique_numeric_ranks[i] - unique_numeric_ranks[i+4] == 4:
                return "Straight"
        # Special case for Ace-low straight
        if set([14, 5, 4, 3, 2]).issubset(unique_numeric_ranks):
            return "Straight"
    
    # Check three of a kind
    if 3 in rank_counts.values():
        return "Three of a Kind"
    
    # Check two pair
    if list(rank_counts.values()).count(2) >= 2:
        return "Two Pair"
    
    # Check one pair
    if 2 in rank_counts.values():
        return "One Pair"
    
    return "High Card"


# check for ante condition
def dealer_has_pair_or_better(dealer_hand, community_cards):
    """
    Checks whether dealer qualifies (pair or better).

    Args:
        dealer_hand (list): dealer's 2 cards
        community_cards (list): community cards

    Returns:
        bool: True if dealer has pair or better, else False
    """
    combined_cards = dealer_hand + community_cards
    hand_strength = get_best_hand(combined_cards)
    stronger_hands = ["One Pair", "Two Pair", "Three of a Kind", "Straight", "Flush",
                      "Full House", "Four of a Kind", "Straight Flush", "Royal Flush"]

    return hand_strength in stronger_hands


def has_blind(blind, player_combination):
    """
    Applies blind payout rules based on player's final hand.

    Args:
        blind (int/float): original blind bet
        player_combination (str): player's hand type

    Returns:
        int/float: updated blind payout amount
    """
    if player_combination == "Straight":
        blind *= 2
    elif player_combination == "Flush":
        blind *= 3
    elif player_combination == "Full House":
        blind *= 4
    elif player_combination == "Four of a Kind":  
        blind *= 11
    elif player_combination == "Straight Flush":
        blind *= 51
    elif player_combination == "Royal Flush":
        blind *= 501

    return blind


def trips_bet(trips, player_combination):
    """
    Calculates the payout of the 'trips' side bet.

    Args:
        trips (int): trips bet amount
        player_combination (str): player's final hand type

    Returns:
        int: payout (positive or negative)
    """
    payout = 0
    
    if player_combination == "Three of a Kind":
        payout += trips * 3
    elif player_combination == "Straight":
        payout += trips * 5
    elif player_combination == "Flush":
        payout += trips * 6
    elif player_combination == "Full House":
        payout += trips * 7
    elif player_combination == "Four of a Kind":
        payout += trips * 20
    elif player_combination == "Straight Flush":
        payout += trips * 40
    elif player_combination == "Royal Flush":
        payout += trips * 50
    else:
        payout -= trips
    
    return payout


def find_straight_high(ranks):
    """
    Finds the highest card in a straight, if any.

    Args:
        ranks (list[int]): list of card ranks in numeric form

    Returns:
        int: high card of straight, or 0 if none
    """
    # Check for Ace-low straight (5-4-3-2-A)
    if {14, 5, 4, 3, 2}.issubset(ranks):
        return 5
    
    # Check normal straights
    for i in range(len(ranks) - 4):
        if ranks[i] - ranks[i+4] == 4:
            return ranks[i]
    
    return 0

# decides kicker / draw
def decider(player_combination, player_final_hand, dealer_combination, dealer_final_hand):
    """
    Resolves ties between player and dealer hands by comparing kickers 
    or applying specific poker rules.

    Args:
        player_combination (str): player's hand type
        player_final_hand (list): player's full set of cards
        dealer_combination (str): dealer's hand type
        dealer_final_hand (list): dealer's full set of cards

    Returns:
        str: "player", "dealer", or "tie"
    """
    # First check if combinations are different
    if player_combination != dealer_combination:
        return None  # This case should be handled by the calling function
    
    rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, 
                   '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
    
    player_counts = Counter(card['rank'] for card in player_final_hand)
    dealer_counts = Counter(card['rank'] for card in dealer_final_hand)
    
    def get_kickers(cards, excluded_ranks=[]):
        return sorted((rank_values[card['rank']] for card in cards 
                     if card['rank'] not in excluded_ranks), reverse=True)
    
    # High Card
    if player_combination == "High Card":
        player_kickers = get_kickers(player_final_hand)[:5]
        dealer_kickers = get_kickers(dealer_final_hand)[:5]
    
    # One Pair
    elif player_combination == "One Pair":
        # Get pair values
        player_pair = max((rank for rank, count in player_counts.items() if count == 2), 
                         key=lambda r: rank_values[r])
        dealer_pair = max((rank for rank, count in dealer_counts.items() if count == 2), 
                         key=lambda r: rank_values[r])
        
        # Compare pairs
        if rank_values[player_pair] > rank_values[dealer_pair]:
            return "player"
        elif rank_values[player_pair] < rank_values[dealer_pair]:
            return "dealer"
        
        # Compare kickers if pairs are equal
        player_kickers = get_kickers(player_final_hand, [player_pair])[:3]
        dealer_kickers = get_kickers(dealer_final_hand, [dealer_pair])[:3]
    
    # Two Pair
    elif player_combination == "Two Pair":
        # Get top two pairs for each player
        player_pairs = sorted((rank_values[rank] for rank, count in player_counts.items() if count == 2), 
                             reverse=True)[:2]
        dealer_pairs = sorted((rank_values[rank] for rank, count in dealer_counts.items() if count == 2), 
                             reverse=True)[:2]
        
        # Compare highest pair
        if player_pairs[0] > dealer_pairs[0]:
            return "player"
        elif player_pairs[0] < dealer_pairs[0]:
            return "dealer"
        
        # Compare second pair if first is equal
        if player_pairs[1] > dealer_pairs[1]:
            return "player"
        elif player_pairs[1] < dealer_pairs[1]:
            return "dealer"
        
        # Compare kicker if both pairs are equal
        excluded = [rank for rank in player_counts if rank_values[rank] in player_pairs]
        player_kickers = get_kickers(player_final_hand, excluded)[:1]
        dealer_kickers = get_kickers(dealer_final_hand, excluded)[:1]
    
    # Three of a Kind
    elif player_combination == "Three of a Kind":
        player_triplet = max((rank for rank, count in player_counts.items() if count == 3), 
                           key=lambda r: rank_values[r])
        dealer_triplet = max((rank for rank, count in dealer_counts.items() if count == 3), 
                           key=lambda r: rank_values[r])
        
        if rank_values[player_triplet] > rank_values[dealer_triplet]:
            return "player"
        elif rank_values[player_triplet] < rank_values[dealer_triplet]:
            return "dealer"
        
        player_kickers = get_kickers(player_final_hand, [player_triplet])[:2]
        dealer_kickers = get_kickers(dealer_final_hand, [dealer_triplet])[:2]
    
    # Straight
    elif player_combination == "Straight":
        player_ranks = sorted({rank_values[card['rank']] for card in player_final_hand}, reverse=True)
        dealer_ranks = sorted({rank_values[card['rank']] for card in dealer_final_hand}, reverse=True)
        
        # Find highest straight for each
        player_high = find_straight_high(player_ranks)
        dealer_high = find_straight_high(dealer_ranks)
        
        if player_high > dealer_high:
            return "player"
        elif player_high < dealer_high:
            return "dealer"
        return "tie"
    
    # Flush
    elif player_combination == "Flush":
        # Get flush cards for each player
        player_suit = Counter(card['suit'] for card in player_final_hand).most_common(1)[0][0]
        dealer_suit = Counter(card['suit'] for card in dealer_final_hand).most_common(1)[0][0]
        
        player_kickers = sorted([rank_values[card['rank']] for card in player_final_hand 
                          if card['suit'] == player_suit], reverse=True)[:5]
        dealer_kickers = sorted([rank_values[card['rank']] for card in dealer_final_hand 
                          if card['suit'] == dealer_suit], reverse=True)[:5]
    
    # Full House
    elif player_combination == "Full House":
        # Compare triplet first
        player_triplet = max((rank_values[rank] for rank, count in player_counts.items() if count == 3))
        dealer_triplet = max((rank_values[rank] for rank, count in dealer_counts.items() if count == 3))
        
        if player_triplet > dealer_triplet:
            return "player"
        elif player_triplet < dealer_triplet:
            return "dealer"
        
        # Compare pair if triplets are equal
        player_pair = max((rank_values[rank] for rank, count in player_counts.items() 
                         if count >= 2 and rank_values[rank] != player_triplet), default=0)
        dealer_pair = max((rank_values[rank] for rank, count in dealer_counts.items() 
                         if count >= 2 and rank_values[rank] != dealer_triplet), default=0)
        
        if player_pair > dealer_pair:
            return "player"
        elif player_pair < dealer_pair:
            return "dealer"
        return "tie"
    
    # Four of a Kind
    elif player_combination == "Four of a Kind":
        player_quad = max((rank_values[rank] for rank, count in player_counts.items() if count == 4))
        dealer_quad = max((rank_values[rank] for rank, count in dealer_counts.items() if count == 4))
        
        if player_quad > dealer_quad:
            return "player"
        elif player_quad < dealer_quad:
            return "dealer"
        
        # Compare kicker
        player_kickers = get_kickers(player_final_hand, 
                                   [rank for rank in player_counts if rank_values[rank] == player_quad])[:1]
        dealer_kickers = get_kickers(dealer_final_hand, 
                                   [rank for rank in dealer_counts if rank_values[rank] == dealer_quad])[:1]
    
    # Straight Flush
    elif player_combination == "Straight Flush":
        player_suit = Counter(card['suit'] for card in player_final_hand).most_common(1)[0][0]
        dealer_suit = Counter(card['suit'] for card in dealer_final_hand).most_common(1)[0][0]
        
        player_ranks = sorted({rank_values[card['rank']] for card in player_final_hand 
                             if card['suit'] == player_suit}, reverse=True)
        dealer_ranks = sorted({rank_values[card['rank']] for card in dealer_final_hand 
                             if card['suit'] == dealer_suit}, reverse=True)
        
        player_high = find_straight_high(player_ranks)
        dealer_high = find_straight_high(dealer_ranks)
        
        if player_high > dealer_high:
            return "player"
        elif player_high < dealer_high:
            return "dealer"
        return "tie"
    
    # Royal Flush
    elif player_combination == "Royal Flush":
        return "tie"
    
    # Compare kickers if still undecided
    for p_kicker, d_kicker in zip(player_kickers, dealer_kickers):
        if p_kicker > d_kicker:
            return "player"
        elif p_kicker < d_kicker:
            return "dealer"
    
    return "tie"


#========================================================================================================
# Functiosn for poker api
def deal_cards(players=1):
    """
    Deals cards for a game round.

    Args:
        players (int): number of players (default 1)

    Returns:
        list: all dealt cards (2 cards per player + 5 community cards)
    """
    deck_copy = deck.copy()
    random.shuffle(deck_copy)
    all_cards = []
    # Each player needs 2 cards, plus 5 community cards
    for i in range(7 + players * 2):
        all_cards.append(deal_card(deck_copy))
    return all_cards


def calculate_game(game_data):
    """
    Determines the outcome of a poker game between player and dealer.

    Args:
        game_data (dict): dictionary containing:
            - "player_cards": player's 2 hole cards
            - "dealer_cards": dealer's 2 hole cards
            - "community_cards": 5 shared cards
            - "ante": ante bet
            - "blind": blind bet
            - "round_when_bet": round number when bet was placed
            - "bet": any additional bet amount

    Returns:
        tuple: (winner, winnings, player_hand_name, dealer_hand_name)
    """
    # Build final 7-card hands
    player_hand = game_data["player_cards"] + game_data["community_cards"]
    dealer_hand = game_data["dealer_cards"] + game_data["community_cards"]

    ante = game_data["ante"]
    blind = game_data["blind"]
    bet_round = game_data["round_when_bet"]

    # evaluate cards
    player_combination = get_best_hand(player_hand)
    dealer_combination = get_best_hand(dealer_hand)

    # If player folded in round 3, dealer wins automatically
    if bet_round == 3:
        return "dealer", -(ante + blind)

    # Ordered winning hand types
    winning_hands = [
        "High Card", "One Pair", "Two Pair", "Three of a Kind", "Straight", "Flush",
        "Full House", "Four of a Kind", "Straight Flush", "Royal Flush"
    ]
    
    # Decide winner
    if winning_hands.index(player_combination) > winning_hands.index(dealer_combination):
        winner = "player"
    elif winning_hands.index(player_combination) == winning_hands.index(dealer_combination):
        # Same category -> use tiebreaker
        result = decider(player_combination, player_hand, dealer_combination, dealer_hand)
        if result == "player": 
            winner = "player"
        elif result == "dealer":
            winner = "dealer"
        else: 
            winner = "tie"
    else:
        winner = "dealer"

    # Special blind/ante rules
    dealer_has_something = dealer_has_pair_or_better(dealer_hand, game_data["community_cards"])
    blind_won = has_blind(blind, player_combination) - blind

    # Calculate winnings
    if winner == "player":
        # Player wins bet + blind bonus + ante if dealer qualifies
        winnings = game_data["bet"] + blind_won + (ante if dealer_has_something else 0)
    elif winner == "dealer":
        # Dealer wins everything
        winnings = -(ante + blind + game_data["bet"])
    else:
        # Tie -> no change
        winnings = 0

    print(winner, winnings, player_combination, dealer_combination)
    print("test")
    return winner, winnings, player_combination, dealer_combination


def trips_payout(iter=1000):
    """
    Simulates 'trips' side bet payout odds over many iterations.

    Args:
        iter (int): number of simulated hands (default 1000)

    Returns:
        None (prints edge and frequency of hands)
    """
    global budget
    budget = 0

    # Track counts of specific qualifying hands
    hand_counts = {
        "Three of a Kind": 0,
        "Straight": 0,
        "Flush": 0,
        "Full House": 0,
        "Four of a Kind": 0,
        "Straight Flush": 0,
        "Royal Flush": 0,
    }

    for i in range(iter):
        trips = 5  # bet size
        deck_copy = deck.copy()
        random.shuffle(deck_copy)
    
        # Deal cards
        player_hand = [deal_card(deck_copy), deal_card(deck_copy)]
        community_cards = [deal_card(deck_copy) for _ in range(5)]
        player_final_hand = player_hand + community_cards
        player_combination = get_best_hand(player_final_hand)

        # Count only hands that qualify
        if player_combination in hand_counts:
            hand_counts[player_combination] += 1
    
        # Add payout for this round
        budget += trips_bet(trips, player_combination)
    
    # Show results
    print(f"Edge {(budget / (trips * iter)) * 100}%")
    print("Hand combination counts:")
    for hand, count in hand_counts.items():
        print(f"{hand}: {count} times")












