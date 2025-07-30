from povezava import ustvari_povezavo

from psycopg2 import sql, errors


def registracija_uporabnika(ime, geslo):
    
    conn, cur = ustvari_povezavo()
    
    try:
        insert_query = sql.SQL(
            "INSERT INTO users (username, password) VALUES (%s, %s)"
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
            
def get_user(ime):
    
    conn, cur = ustvari_povezavo()
    
    try:
        select_query = sql.SQL(
            "SELECT * FROM uporabniki WHERE uporabnik_id = %s"
        )
        cur.execute(select_query, (ime,))
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
            "SELECT stanje FROM denarnica WHERE uporabnik_id = %s"
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
            "SELECT vrednostni_papir_id, kolicina FROM portfelji WHERE uporabnik_id = %s"
        )
        cur.execute(select_query, (user_id,))
        portfolio = cur.fetchall()
        return portfolio
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
            "SELECT stanje FROM denarnica WHERE uporabnik_id = %s"
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
            "INSERT INTO transakcije (uporabnik_id, vrednostni_papir_id, kolicina, vrednost) VALUES (%s, %s, %s, %s)"
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
            "UPDATE denarnica SET stanje = stanje + %s WHERE uporabnik_id = %s"
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
    
    conn, cur = ustvari_povezavo()
    
    try:
        update_query = sql.SQL(
            "UPDATE portfelji SET kolicina = %s, vrednost = %s WHERE uporabnik_id = %s AND vrednostni_papir_id = %s"
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