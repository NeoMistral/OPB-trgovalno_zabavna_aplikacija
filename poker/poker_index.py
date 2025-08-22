import psycopg2
from datetime import datetime
import time
import os
import baze.povezava as povezava

# Uteži delnic
utezi = {
    'AAPL': 0.05, 'MSFT': 0.05, 'NVDA': 0.04, 'AMZN': 0.04, 'GOOGL': 0.04,
    'META': 0.03, 'BRK.B': 0.03, 'TSLA': 0.03, 'UNH': 0.03, 'JNJ': 0.03,
    'V': 0.03, 'XOM': 0.03, 'JPM': 0.03, 'PG': 0.02, 'MA': 0.02, 'LLY': 0.02,
    'HD': 0.02, 'AVGO': 0.02, 'CVX': 0.02, 'KO': 0.01, 'MRK': 0.01,
    'PEP': 0.01, 'ABBV': 0.01, 'BAC': 0.01, 'COST': 0.01, 'MCD': 0.01,
    'ORCL': 0.01, 'EOG': 0.01, 'RTX': 0.01
}

def multiplier(hand):
    """
    Returns the multiplier for a given poker hand.

    Args:
        hand (str): Name of the poker hand (e.g., "Full House", "Royal Flush").

    Returns:
        float: Multiplier value. Higher for stronger hands, 0 if unknown.
    """
    hand = (hand or "").lower()
    return {
        'Royal Flush': 500,
        'Straight Flush': 50,
        'Four of a Kind': 10,
        'Full House': 3,
        'Flush': 1.5,
        'Straight': 1
    }.get(hand, 0)

def get_data(bet, player_combo, dealer_combo):
    """
    Inserts a new poker game record into the database.

    Args:
        bet (float): Amount of the player's bet.
        player_combo (str): Player's poker hand.
        dealer_combo (str): Dealer's poker hand.

    Returns:
        None
    """
    try:
        conn, cur = povezava.ustvari_povezavo()
        cur.execute("""
            INSERT INTO poker (bet, player_combo, dealer_combo)
            VALUES (%s, %s, %s)
        """, (bet, str(player_combo), str(dealer_combo)))
        conn.commit()

    except Exception as e:
        print("Napaka pri zapisu v bazo:", e)
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def izracunaj_bet(simbol: str, stevilo: int) -> float:
    """
    Calculates the total bet value based on the latest stock price.

    Args:
        simbol (str): Stock symbol (e.g., "AAPL").
        stevilo (int): Number of shares to calculate with.

    Returns:
        float: Total bet value (price * quantity). Returns 0 if stock not found.
    """

    conn = None
    bet = 0.0
    try:
        conn, cur = povezava.ustvari_povezavo()
        cur.execute("""
            SELECT trenutna_cena 
            FROM delnice 
            WHERE simbol = %s
            ORDER BY datum DESC
            LIMIT 1;
        """, (simbol,))
        result = cur.fetchone()

        if result:
            trenutna_cena = float(result[0])
            bet = trenutna_cena * stevilo
            print(f"✅ {stevilo}x {simbol} po {trenutna_cena:.2f} = {bet:.2f} €")
        else:
            print(f"❌ Ni podatkov za delnico: {simbol}")   

    except Exception as e:
        print("❌ Napaka pri izračunu:", e)
    finally:
        if conn:
            conn.close()

    return bet


def osvezi_indeks():
    """
    Refreshes the POKER index by combining stock market data with poker results.

    Steps:
        1. Fetches the latest stock prices and applies predefined weights.
        2. Calculates the base price of the POKER index.
        3. Adjusts market cap based on active poker game results.
        4. Updates the index price and market cap in the database.
        5. Archives completed poker games.

    Returns:
        None
    """
    conn = None
    try:
            conn, cur = povezava.ustvari_povezavo()
            cur.execute("""
                SELECT simbol, trenutna_cena
                FROM (
                    SELECT simbol, trenutna_cena, ROW_NUMBER() OVER (PARTITION BY simbol ORDER BY datum DESC) as rn
                    FROM delnice
                ) sub
                WHERE rn = 1
            """)
            cene = cur.fetchall()
            cena_map = {simbol: float(cena) for simbol, cena in cene if simbol in utezi}

            # Osnovna cena
            cena_osnove = sum(
                cena_map[simbol] * utezi[simbol]
                for simbol in utezi if simbol in cena_map
            )
            cur.execute("SELECT market_cap FROM index_token WHERE simbol = 'POKER'")
            result = cur.fetchone()
            if not result:
                market_cap = 10_000_000
                cur.execute("""
                    INSERT INTO index_token (simbol, market_cap, trenutna_cena)
                    VALUES ('POKER', %s, %s)
                """, (market_cap, cena_osnove))
            else:
                market_cap = float(result[0])

            # Aktivne igre
            cur.execute("SELECT bet, player_combo, dealer_combo FROM poker")
            igre = cur.fetchall()
            delta = 0
            for bet, player, dealer in igre:
                vpliv = float(bet) * (1 + multiplier(dealer) - multiplier(player)) / 200
                delta += vpliv

            # Nova cena
            nov_market_cap = market_cap + delta
            nova_cena = cena_osnove * (nov_market_cap / 10_000_000)

            cur.execute("DELETE FROM delnice WHERE simbol = 'POKER'")
            cur.execute("""
                INSERT INTO delnice (
                    simbol, datum, trenutna_cena, odprtje, najvisja, najnizja,
                    zaprtje_prejsnji, sprememba, sprememba_procent, volumen
                ) VALUES (%s, %s, %s, NULL, NULL, NULL, NULL, NULL, NULL, NULL)
            """, ('POKER', datetime.now(), nova_cena))

            # index_token kot osnova za vpliv poker iger
            cur.execute("""
                UPDATE index_token SET
                    market_cap = %s,
                    trenutna_cena = %s
                WHERE simbol = 'POKER'
            """, (nov_market_cap, nova_cena))

            # Arhiv
            if igre:
                cur.executemany("""
                    INSERT INTO arhiv (tip, bet, player_combo, dealer_combo)
                    VALUES ('POKER', %s, %s, %s)
                """, igre)
                cur.execute("DELETE FROM poker")

            conn.commit()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Indeks osvežen — Cena: {nova_cena:.2f} €, Market Cap: {nov_market_cap:.2f} €")

    except Exception as e:
        print("❌ Napaka pri osveževanju indeksa:", e)
    finally:
        if conn:
            conn.close()

