import finnhub
import psycopg2
from dotenv import load_dotenv
import os
from datetime import datetime
import time

load_dotenv(dotenv_path="key.env")

api_key = os.getenv("FINNHUB_API_KEY")
finnhub_client = finnhub.Client(api_key=api_key)

symbols = [
    'AAPL', 'MSFT', 'NVDA', 'AMZN', 'GOOGL', 'META', 'BRK.B', 'TSLA',
    'UNH', 'JNJ', 'V', 'XOM', 'JPM', 'PG', 'MA', 'LLY', 'HD', 'AVGO',
    'CVX', 'KO', 'MRK', 'PEP', 'ABBV', 'BAC', 'COST', 'MCD', 'ORCL', 'EOG', 'RTX'
]


def get_stock_data(symbol):
    try:
        quote = finnhub_client.quote(symbol)
        company = finnhub_client.company_profile2(symbol=symbol)

        if not quote or 'c' not in quote:
            raise ValueError(f"Neveljaven odgovor za {symbol}: {quote}")

        return {
            'symbol': symbol,
            'current': quote['c'],
            'open': quote['o'],
            'high': quote['h'],
            'low': quote['l'],
            'previous_close': quote['pc'],
            'change': quote['d'],
            'percent_change': quote['dp'],
            'volume': quote.get('v', 0),
            'company_name': company.get('name', ''),
            'timestamp': datetime.fromtimestamp(quote['t']) if quote['t'] else datetime.now()
        }
    except Exception as e:
        print(f"❌ Napaka pri pridobivanju podatkov za {symbol}: {e}")
        return None


def save_to_db(data):
    if not data:
        return

    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        cur = conn.cursor()

        query = """
        INSERT INTO delnice_temp (
            simbol, datum, trenutna_cena, odprtje, najvisja, najnizja,
            zaprtje_prejsnji, sprememba, sprememba_procent, volumen
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        cur.execute(query, (
            data['symbol'],
            data['timestamp'],
            data['current'],
            data['open'],
            data['high'],
            data['low'],
            data['previous_close'],
            data['change'],
            data['percent_change'],
            data['volume']
        ))

        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Napaka pri shranjevanju v delnice_temp: {e}")


def main_loop(interval_seconds=30):
    while True:
        print(f"\n🔁 Začetek osveževanja podatkov ob {datetime.now()}")

        try:
            conn = psycopg2.connect(
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT")
            )
            cur = conn.cursor()
            cur.execute("TRUNCATE delnice_temp;")
            conn.commit()
            cur.close()
            conn.close()
            print("🧹 delnice_temp počiščena.")
        except Exception as e:
            print(f"❌ Napaka pri čiščenju delnice_temp: {e}")

        for symbol in symbols:
            data = get_stock_data(symbol)
            if data:
                save_to_db(data)

        try:
            conn = psycopg2.connect(
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT")
            )
            cur = conn.cursor()
            cur.execute("DELETE FROM delnice WHERE simbol != 'POKER';")
            cur.execute("INSERT INTO delnice SELECT * FROM delnice_temp;")
            conn.commit()
            cur.close()
            conn.close()

            print("✅ Novi podatki uspešno prestavljeni v delnice.")

        except Exception as e:
            print(f"❌ Napaka pri kopiranju v delnice: {e}")

        print(f"⏳ Čakam {interval_seconds} sekund pred naslednjo iteracijo.")
        time.sleep(interval_seconds)


if __name__ == "__main__":
    try:
        main_loop(interval_seconds=30) 
    except KeyboardInterrupt:
        print("\n🛑 Uporabnik je prekinil izvajanje. Izhod.")