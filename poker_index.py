import psycopg2
from dotenv import load_dotenv
from datetime import datetime
import os

from collections import defaultdict

load_dotenv(dotenv_path="key.env")


def multiplier(hand):
    hand = hand.lower()
    if hand == 'royal flush':
        return 500
    elif hand == 'straight flush':
        return 50
    elif hand == 'four of a kind':
        return 10
    elif hand == 'full house':
        return 3
    elif hand == 'flush':
        return 1.5
    elif hand == 'straight':
        return 1
    else:
        return 0


def index():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        cur = conn.cursor()

        cur.execute("SELECT simbol, trenutna_cena FROM delnice")
        trenutne = cur.fetchall()

        cur.execute("SELECT simbol, trenutna_cena FROM arhiv")
        prejsnje = cur.fetchall()

        cena_map_nova = {sim: cena for sim, cena in trenutne}
        cena_map_stara = {sim: cena for sim, cena in prejsnje}

        spremembe = []
        for sim in cena_map_nova:
            if sim in cena_map_stara and cena_map_stara[sim] > 0:
                sprememba = (cena_map_nova[sim] - cena_map_stara[sim]) / cena_map_stara[sim]
                spremembe.append(sprememba)

        povprecna_sprememba = sum(spremembe) / len(spremembe) if spremembe else 0

        cur.execute("SELECT trenutna_cena, market_cap, supply FROM index WHERE simbol = 'INDEX'")
        index_row = cur.fetchone()

        trenutna_cena_indeksa, star_market_cap, supply = index_row

        cur.execute("SELECT bet, player_hand, dealer_hand FROM igre")
        igre = cur.fetchall()

        poker_prispevek = 0
        for bet, player, dealer in igre:
            bet_vpliv = bet / 200
            izplacilo_dealer = multiplier(dealer)
            izplacilo_player = multiplier(player)
            razlika = (izplacilo_dealer - izplacilo_player) # /200 
            poker_prispevek += bet_vpliv + razlika

        nov_market_cap = (star_market_cap  + poker_prispevek) * (1 + povprecna_sprememba)
        nova_cena = nov_market_cap / supply

        cur.execute("""
            UPDATE index SET
                trenutna_cena = %s,
                market_cap = %s,
                datum = NOW()
            WHERE simbol = 'INDEX'
        """, (nova_cena, nov_market_cap))


        conn.commit()
        print(f"✅ Indeks posodobljen: nova cena = {nova_cena:.2f} €, market cap = {nov_market_cap:.2f} €")

    except Exception as e:
        print("❌ Napaka pri posodobitvi indeksa:", e)

    finally:
        if conn:
            conn.close()