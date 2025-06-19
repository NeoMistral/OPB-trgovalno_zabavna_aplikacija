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
            "SELECT simbol FROM delinice"
        )
        cur.execute("SELECT name FROM employees")

# Fetch all results
        rows = cur.fetchall()

# Optional: Flatten to a list of values
        names = [row[0] for row in rows]
        # cur.execute(select_query)
        # prices = cur.fetchall()
        return names
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