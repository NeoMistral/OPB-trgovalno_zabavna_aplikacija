from baze.povezava import ustvari_povezavo

from psycopg2 import sql, errors


def registracija_uporabnika(ime, geslo):
    """
    Registers a new user in the database with an initial balance and empty portfolio.

    Args:
        ime (str): Username
        geslo (str): Password

    Returns:
        bool: True if registration was successful, False if username already exists
    """
    conn, cur = ustvari_povezavo()
    
    try:
        insert_query = sql.SQL(
            "INSERT INTO uporabniki (uporabnisko_ime, geslo, stanje, vrednostni_portfeljev) VALUES (%s, %s, 100000, 0)"
        )
        cur.execute(insert_query, (ime, geslo))
        conn.commit()
        print("User registered successfully.")
        return True
    except errors.UniqueViolation:
        print("Username already exists.")
        return False
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()
            
def get_user(uporabnisko_ime, geslo):
    conn, cur = ustvari_povezavo()
    """
    Retrieves a user from the database.

    Args:
        uporabnisko_ime (str): Username
        geslo (str): Password

    Returns:
        tuple | None: User record if found, otherwise None
    """
    try:
        select_query = sql.SQL(
            "SELECT * FROM uporabniki WHERE uporabnisko_ime = %s AND geslo = %s"
        )
        cur.execute(select_query, (uporabnisko_ime, geslo))
        user = cur.fetchone()
        return user
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()
            
def get_stock_prices():
    """
    Retrieves all stock symbols and their current prices.

    Returns:
        list[dict]: A list of dictionaries with keys:
                    - 'symbol': stock symbol
                    - 'price': stock price
    """    
    conn, cur = ustvari_povezavo()
    
    try:
        select_query = sql.SQL(
            "SELECT trenutna_cena FROM delnice"
        )
        cur.execute("SELECT simbol FROM delnice")

# Fetch all results
        rows = cur.fetchall()

# Optional: Flatten to a list of values
        names = [row[0] for row in rows]
        cur.execute(select_query)
        prices = cur.fetchall()
        prices = [row[0] for row in prices]
        out = []
        for name, price in zip(names, prices):
            out.append({'symbol': name, 'price': float(price)})

        return out[:30]
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()
            
def get_user_balance(user_id):
    """
    Retrieves a user's account balance.

    Args:
        user_id (int): User ID

    Returns:
        float | None: Balance if user exists, else None
    """    
    conn, cur = ustvari_povezavo()
    
    try:
        select_query = sql.SQL(
            "SELECT stanje FROM uporabniki WHERE uporabnik_id = %s"
        )
        cur.execute(select_query, (user_id,))
        balance = cur.fetchone()
        return balance[0] if balance else None
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()
            
def get_user_portfolio(user_id):
    """
    Retrieves a user's portfolio (symbol + quantity).

    Args:
        user_id (int): User ID

    Returns:
        list[dict]: List of dictionaries with keys:
                    - 'symbol'
                    - 'amount'
    """
    conn, cur = ustvari_povezavo()

    try:
        select_query = sql.SQL(
            """
            SELECT simbol, kolicina FROM portfelji WHERE uporabnik_id = %s ORDER BY portfelj_id
            """
        )
        cur.execute(select_query, (user_id,))
        rows = cur.fetchall()

        # Format the result as a list of dictionaries
        portfolio = [{"symbol": row[0], "amount": row[1]} for row in rows]
        return portfolio
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        if conn:
            cur.close()
            conn.close()
            
def get_user_portfolio_all(user_id):
    """
    Retrieves full portfolio (symbol, quantity, value).

    Args:
        user_id (int): User ID

    Returns:
        list[dict]: List with keys:
                    - 'symbol'
                    - 'amount'
                    - 'value'
    """
    conn, cur = ustvari_povezavo()

    try:
        select_query = sql.SQL(
            """
            SELECT simbol, kolicina, vrednost FROM portfelji WHERE uporabnik_id = %s ORDER BY portfelj_id
            """
        )
        cur.execute(select_query, (user_id,))
        rows = cur.fetchall()

        # Format the result as a list of dictionaries
        portfolio = [{"symbol": row[0], "amount": row[1], "value": float(row[2])} for row in rows]
        return portfolio
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        if conn:
            cur.close()
            conn.close()
            
            
def get_user_balance(user_id):
    """
    Inserts a transaction record for a user.

    Args:
        user_id (int): User ID
        stock_id (str): Stock symbol
        quantity (int): Quantity of stock
        value (float): Transaction value
    """    
    conn, cur = ustvari_povezavo()
    
    try:
        select_query = sql.SQL(
            "SELECT stanje FROM uporabniki WHERE uporabnik_id = %s"
        )
        cur.execute(select_query, (user_id,))
        balance = cur.fetchone()
        return balance[0] if balance else None
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()

def add_transaction(user_id, stock_id, quantity, value):
    """
    Inserts a transaction record for a user.

    Args:
        user_id (int): User ID
        stock_id (str): Stock symbol
        quantity (int): Quantity of stock
        value (float): Transaction value
    """   
    conn, cur = ustvari_povezavo()
    
    try:
        insert_query = sql.SQL(
            "INSERT INTO transakcije (uporabnik_id, simbol, kolicina, vrednost) VALUES (%s, %s, %s, %s)"
        )
        cur.execute(insert_query, (user_id, stock_id, quantity, value))
        conn.commit()
        print("Transaction added successfully.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()         
            
def update_user_balance(user_id, balance_change):
    """
    Updates a user's balance by adding/subtracting a value.

    Args:
        user_id (int): User ID
        balance_change (float): Amount to change balance
    """    
    conn, cur = ustvari_povezavo()
    
    try:
        update_query = sql.SQL(
            "UPDATE uporabniki SET stanje = stanje + %s WHERE uporabnik_id = %s"
        )
        cur.execute(update_query, (balance_change, user_id))
        conn.commit()
        print("User balance updated by change:", balance_change)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()
            
            
def update_portfolio(user_id, stock_id, quantity, value):
    """
    Updates a user's portfolio (quantity + value).

    Args:
        user_id (int): User ID
        stock_id (str): Stock symbol
        quantity (int): Quantity change
        value (float): Updated stock value
    """    
    conn, cur = ustvari_povezavo()
    
    try:
        update_query = sql.SQL(
            "UPDATE portfelji SET kolicina = kolicina + %s, vrednost = %s WHERE uporabnik_id = %s AND simbol = %s"
        )
        cur.execute(update_query, (quantity, value, user_id, stock_id))
        conn.commit()
        print("Portfolio updated successfully.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()
            
def update_portfolio_brez_cene(user_id, stock_id, quantity):
    """
    Updates only the quantity of a stock in the user's portfolio.

    Args:
        user_id (int): User ID
        stock_id (str): Stock symbol
        quantity (int): New stock quantity
    """    
    conn, cur = ustvari_povezavo()
    print(quantity)
    try:
        update_query = sql.SQL(
            "UPDATE portfelji SET kolicina = %s WHERE uporabnik_id = %s AND simbol = %s"
        )
        cur.execute(update_query, (quantity, user_id, stock_id))
        conn.commit()
        print("Portfolio updated successfully.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()

def can_buy(user_id, quantity, price):
    """
    Checks if a user has enough balance to buy a given quantity of stock.

    Returns:
        bool: True if user can buy, else False
    """
    if get_user_balance(user_id) < quantity * price:
        return False
    return True

def can_sell(user, symbol, quantity):
    """
    Checks if a user has enough of a stock to sell.

    Returns:
        bool: True if user can sell, else False
    """
    quant = [item for item in get_user_portfolio(user) if item["symbol"] == symbol]
    stock = quant[0] if quant else None
    if not stock:
        return False
    if stock["amount"] < quantity:
        return False
    return True

def check_if_user_exists(uporabnisko_ime, geslo):
    """
    Checks if a user with given username and password exists.

    Returns:
        bool: True if user exists, else False
    """
    conn, cur = ustvari_povezavo()

    try:
        select_query = sql.SQL(
            "SELECT 1 FROM uporabniki WHERE uporabnisko_ime = %s AND geslo = %s LIMIT 1"
        )
        cur.execute(select_query, (uporabnisko_ime, geslo))
        return cur.fetchone() is not None
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if conn:
            cur.close()
            conn.close()
            
def get_user_id(uporabnisko_ime):
    """
    Retrieves the user ID for a given username.

    Returns:
        int | None: User ID if found, else None
    """
    conn, cur = ustvari_povezavo()
    
    try:
        select_query = sql.SQL(
            "SELECT uporabnik_id FROM uporabniki WHERE uporabnisko_ime = %s"
        )
        cur.execute(select_query, (uporabnisko_ime,))
        result = cur.fetchone()
        return result[0] if result else None
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()
            
def insert_user_stocks(user_id):
    """
    Inserts default stock entries into a user's portfolio with quantity=0 and value=0.

    Args:
        user_id (int): User ID
    """
    conn, cur = ustvari_povezavo()
    
    simboli = [
        "POKER","AAPL","MSFT","NVDA","AMZN","GOOGL","META","BRK.B","TSLA","UNH","JNJ",
        "V","XOM","JPM","PG","MA","LLY","HD","AVGO","CVX","KO","MRK","PEP","ABBV","BAC","COST","MCD",
        "ORCL","EOG","RTX"
    ]
    
    try:
        insert_query = sql.SQL("""
            INSERT INTO portfelji (uporabnik_id, simbol, kolicina, vrednost)
            VALUES (%s, %s, 0, 0)
        """)
        rows = [(user_id, simbol) for simbol in simboli]
        cur.executemany(insert_query, rows)
        
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()