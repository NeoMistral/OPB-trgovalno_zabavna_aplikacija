import finnhub
import psycopg2
from dotenv import load_dotenv
import os
from datetime import datetime
import time
from povezava import ustvari_povezavo
from poker_index import osvezi_indeks

# Load API keys and secrets from key.env file
load_dotenv(dotenv_path="key.env")

# Initialize Finnhub API client
api_key = os.getenv("FINNHUB_API_KEY")
finnhub_client = finnhub.Client(api_key=api_key)

# List of tracked stock symbols (used in index calculation)
symbols = [
    'AAPL', 'MSFT', 'NVDA', 'AMZN', 'GOOGL', 'META', 'BRK.B', 'TSLA',
    'UNH', 'JNJ', 'V', 'XOM', 'JPM', 'PG', 'MA', 'LLY', 'HD', 'AVGO',
    'CVX', 'KO', 'MRK', 'PEP', 'ABBV', 'BAC', 'COST', 'MCD', 'ORCL', 'EOG', 'RTX'
]


def get_stock_data(symbol):
    """
    Fetches stock market data for a given symbol from Finnhub API.

    Args:
        symbol (str): Stock ticker symbol (e.g., "AAPL").

    Returns:
        dict | None: Dictionary with stock data including price, volume, 
                     and company info. Returns None if data retrieval fails.

    Example return:
        {
            'symbol': 'AAPL',
            'current': 150.25,
            'open': 149.50,
            'high': 151.00,
            'low': 148.90,
            'previous_close': 149.80,
            'change': 0.45,
            'percent_change': 0.30,
            'volume': 55000000,
            'company_name': 'Apple Inc.',
            'timestamp': datetime(2025, 8, 22, 15, 30, 0)
        }
    """
    try:
        quote = finnhub_client.quote(symbol)  # Real-time quote
        company = finnhub_client.company_profile2(symbol=symbol)  # Company profile

        if not quote or 'c' not in quote:
            raise ValueError(f"Invalid response for {symbol}: {quote}")

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
        print(f"❌ Error fetching stock data for {symbol}: {e}")
        return None


def save_to_db(data):
    """
    Saves stock data into the temporary table `delnice_temp`.

    Args:
        data (dict): Dictionary containing stock market data 
                     as returned by `get_stock_data`.

    Returns:
        None
    """
    if not data:
        return

    try:
        conn, cur = ustvari_povezavo()

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
        print(f"❌ Error saving stock data to delnice_temp: {e}")


def main_loop(interval_seconds=30):
    """
    Main loop that periodically fetches stock data, updates the database,
    and recalculates the POKER index.

    Steps:
        1. Clears the temporary table `delnice_temp`.
        2. Fetches stock data for all tracked symbols from Finnhub.
        3. Saves fresh data into `delnice_temp`.
        4. Moves data into the main `delnice` table (excluding POKER).
        5. Refreshes the POKER index using poker game results.
        6. Waits before repeating the cycle.

    Args:
        interval_seconds (int): Time interval in seconds between updates.

    Returns:
        None
    """
    while True:
        print(f"\n🔁 Starting refresh cycle at {datetime.now()}")

        # Step 1: Clear temporary stock data table
        try:
            conn, cur = ustvari_povezavo()
            cur.execute("TRUNCATE delnice_temp;")
            conn.commit()
            cur.close()
            conn.close()
            print("🧹 delnice_temp cleared.")
        except Exception as e:
            print(f"❌ Error clearing delnice_temp: {e}")

        # Step 2–3: Fetch data and save to temporary table
        for symbol in symbols:
            data = get_stock_data(symbol)
            if data:
                save_to_db(data)

        # Step 4: Move updated data to the main table
        try:
            conn, cur = ustvari_povezavo()
            cur.execute("DELETE FROM delnice WHERE simbol != 'POKER';")
            cur.execute("INSERT INTO delnice SELECT * FROM delnice_temp;")
            conn.commit()
            cur.close()
            conn.close()
            print("✅ New stock data successfully moved to delnice.")
        except Exception as e:
            print(f"❌ Error copying data to delnice: {e}")

        # Step 5: Refresh poker-based index
        try:
            osvezi_indeks()
        except Exception as e:
            print(f"❌ Error refreshing POKER index: {e}")

        # Step 6: Wait before next refresh
        print(f"⏳ Waiting {interval_seconds} seconds before next cycle.")
        time.sleep(interval_seconds)


if __name__ == "__main__":
    print("▶️ Starting main loop – refreshing every 30 seconds.")
    try:
        main_loop(interval_seconds=30)
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user. Exiting.")
