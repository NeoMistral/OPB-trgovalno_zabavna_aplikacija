import psycopg2
from dotenv import load_dotenv
from datetime import datetime
import time
import os

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


def update_index():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        cur = conn.cursor()

        cur.execute("""
            SELECT simbol, trenutna_cena, datum 
            FROM delnice 
            ORDER BY datum DESC
            LIMIT 1000
        """)
        rows = cur.fetchall()

        cena_map_nova = {}
        cena_map_stara = {}
        for sim, cena, _ in rows:
            if sim not in cena_map_nova:
                cena_map_nova[sim] = cena
            elif sim not in cena_map_stara:
                cena_map_stara[sim] = cena

        spremembe = []
        for sim in cena_map_nova:
            if sim in cena_map_stara and cena_map_stara[sim] > 0:
                sprememba = (cena_map_nova[sim] - cena_map_stara[sim]) / cena_map_stara[sim]
                spremembe.append(sprememba)

        povprecna_sprememba = sum(spremembe) / len(spremembe) if spremembe else 0


        cur.execute("SELECT trenutna_cena, market_cap FROM index_token WHERE simbol = 'POKER'")
        index_row = cur.fetchone()
        trenutna_cena_indeksa, star_market_cap = index_row

        cur.execute("SELECT bet, player_hand, dealer_hand FROM poker")
        igre = cur.fetchall()

        # Vse igre shranimo v arhiv
        cur.executemany("""
            INSERT INTO arhiv (tip, bet, player_hand, dealer_hand)
            VALUES ('POKER', %s, %s, %s)
        """, igre)

        # Formula
        poker_prispevek = 0
        for bet, player, dealer in igre:
            bet_vpliv = bet / 200
            izplacilo_dealer = multiplier(dealer)
            izplacilo_player = multiplier(player)
            razlika = (izplacilo_dealer - izplacilo_player) / 200
            poker_prispevek += bet_vpliv + razlika

        nov_market_cap = (star_market_cap + poker_prispevek) * (1 + povprecna_sprememba)
        nova_cena = nov_market_cap

        # Posodobimo
        cur.execute("""
            UPDATE index_token SET
                trenutna_cena = %s,
                market_cap = %s
            WHERE simbol = 'POKER'
        """, (nova_cena, nov_market_cap))

        # Počistimo
        cur.execute("DELETE FROM poker")

        conn.commit()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ INDEX posodobljen: {nova_cena:.2f} € (market cap: {nov_market_cap:.2f} €)")

    except Exception as e:
        print("❌ Napaka pri posodobitvi indeksa:", e)

    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("▶️ Začenjam sinhronizacijo indeksa z delnicami")
    while True:
        start_time = time.time()
        update_index()
        elapsed = time.time() - start_time
        time.sleep(max(0, 30 - elapsed))  
