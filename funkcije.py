from povezava import ustvari_povezavo

from psycopg2 import sql, errors


def registracija_uporabnika(ime, geslo):
    
    conn, cur = ustvari_povezavo()
    
    try:
        insert_query = sql.SQL(
            "INSERT INTO uporabniki (uporabnisko_ime, geslo, stanje, vrednostni_portfeljev) VALUES (%s, %s, 10000, 0)"
        )
        cur.execute(insert_query, (ime, geslo))
        conn.commit()
        print("User registered successfully.")
    except errors.UniqueViolation:
        print("Username already exists.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()
            
def get_user(uporabnisko_ime, geslo):
    conn, cur = ustvari_povezavo()

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

        return out[:29]
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()
            
def get_user_balance(user_id):
    
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
    conn, cur = ustvari_povezavo()

    try:
        select_query = sql.SQL(
            """
            SELECT vrednostni_papir_id, kolicina FROM portfelji WHERE uporabnik_id = %s
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
            
            
def get_user_balance(user_id):
    
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
            
            
# def update_portfolio(user_id, stock_id, quantity, value):
    
#     conn, cur = ustvari_povezavo()
    
#     try:
#         update_query = sql.SQL(
#             "UPDATE portfelji SET kolicina = %s, vrednost = %s WHERE uporabnik_id = %s AND vrednostni_papir_id = %s"
#         )
#         cur.execute(update_query, (quantity, value, user_id, stock_id))
#         conn.commit()
#         print("Portfolio updated successfully.")
#     except Exception as e:
#         print(f"Error: {e}")
#     finally:
#         if conn:
#             cur.close()
#             conn.close()
            
def update_portfolio_brez_cene(user_id, stock_id, quantity):
    
    conn, cur = ustvari_povezavo()
    
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
    if get_user_balance(user_id) < quantity * price:
        return False
    return True

def can_sell(user, symbol, quantity):
    quant = [item for item in get_user_portfolio(user) if item[0] == symbol]
    stock = quant[0] if quant else None
    if not stock:
        return False
    if stock["amount"] < quantity:
        return False
    return True

def check_if_user_exists(uporabnisko_ime, geslo):
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
            
def insert_user_stocks(uporabnisko_ime):
    conn, cur = ustvari_povezavo()
    
    simboli = [
        "POKER","AAPL","MSFT","NVDA","AMZN","GOOGL","META","BRK.B","TSLA","UNH","JNJ",
        "V","XOM","JPM","PG","MA","LLY","HD","AVGO","CVX","KO","MRK","PEP","ABBV","BAC","COST","MCD",
        "ORCL","EOG","RTX"
    ]
    
    try:
        insert_query = sql.SQL("""
            INSERT INTO portfelji (uporabnisko_ime, simbol, kolicina, vrednost)
            VALUES (%s, %s, 0, 0)
        """)
        rows = [(uporabnisko_ime, simbol) for simbol in simboli]
        cur.executemany(insert_query, rows)
        
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()