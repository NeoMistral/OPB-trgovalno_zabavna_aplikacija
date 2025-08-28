import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

import config as config

database = config.database
host = config.host
port = config.port
user = config.user
password = config.password
conn = None
cur = None
try:

    conn = psycopg2.connect(
        database=database, 
        host=host, 
        port=port, 
        user=user, 
        password=password)

    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # drop_uporabniki = "DROP TABLE IF EXISTS Uporabniki CASCADE;"
    # drop_denarnica = "DROP TABLE IF EXISTS Denarnica CASCADE;"
    # drop_vrednostni_papirji = "DROP TABLE IF EXISTS vrednostni_papirji CASCADE;"
    # drop_portfelji = "DROP TABLE IF EXISTS Portfelji CASCADE;"
    drop_transakcije = "DROP TABLE IF EXISTS Transakcije CASCADE;"
    cur.execute(drop_transakcije)
    # cur.execute(drop_portfelji)
    # cur.execute(drop_denarnica)
    # cur.execute(drop_uporabniki)
    # cur.execute(drop_vrednostni_papirji)
    # za commentiranje uporabi ctrl+'

    # SQL command to create table "Uporabniki"
    create_uporabniki = """
    CREATE TABLE IF NOT EXISTS Uporabniki (
        uporabnik_id SERIAL PRIMARY KEY,
        uporabnisko_ime VARCHAR(50) NOT NULL UNIQUE,
        geslo VARCHAR(100) NOT NULL,
        stanje DECIMAL(10, 2) NOT NULL,
        vrednostni_portfeljev INTEGER NOT NULL,
    );
    """
    
    # create_denarnica = """
    # CREATE TABLE IF NOT EXISTS Denarnica (
    #     denarnica_id SERIAL PRIMARY KEY,
    #     uporabnik_id INTEGER NOT NULL,
    #     vrednostni_portfeljev INTEGER NOT NULL,
    #     stanje DECIMAL(10, 2) NOT NULL,
    #     FOREIGN KEY (uporabnik_id) REFERENCES Uporabniki(uporabnik_id)
    # );
    # """
    
    # create_vrednostni_papirji = """
    # CREATE TABLE IF NOT EXISTS Vrednostni_papirji (
    #     vrednostni_papir_id INTEGER PRIMARY KEY,
    #     market_cap INTEGER NOT NULL,
    #     cena DECIMAL(10, 2) NOT NULL
    # );
    # """
    
    # SQL command to create table "Transakcije"
    create_transakcije = """
    CREATE TABLE IF NOT EXISTS Transakcije (
        transakcija_id SERIAL PRIMARY KEY,
        simbol varchar(10) NOT NULL,
        uporabnik_id INTEGER NOT NULL,
        kolicina INTEGER NOT NULL,
        vrednost DECIMAL(10, 2) NOT NULL,
        datum TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (uporabnik_id) REFERENCES Uporabniki(uporabnik_id)
    );
    """
    # SQL command to create table "Portfelji"
    create_portfelji = """
    CREATE TABLE IF NOT EXISTS Portfelji (
        portfelj_id SERIAL PRIMARY KEY,
        uporabnik_id INTEGER NOT NULL,
        simbol VARCHAR(10) NOT NULL,
        kolicina INTEGER NOT NULL,
        vrednost DECIMAL(10, 2) NOT NULL,
        FOREIGN KEY (uporabnik_id) REFERENCES Uporabniki(uporabnik_id)
    );
    """
    # SQL command to create table "Poker"
    create_poker = """
    CREATE TABLE IF NOT EXISTS Poker (
        igrana_roka_id SERIAL PRIMARY KEY,
        uporabnik_id INTEGER NOT NULL,
        vložek DECIMAL(10, 2) NOT NULL,
        vrednostni_papir_id INTEGER NOT NULL,
        cas TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        izkupicek DECIMAL(10, 2) NOT NULL,
        FOREIGN KEY (vrednostni_papir_id) REFERENCES delnice(vrednostni_papir_id),
        FOREIGN KEY (uporabnik_id) REFERENCES Uporabniki(uporabnik_id)
    );
    """
    # cur.execute(create_uporabniki)
    # cur.execute(create_denarnica)
    # cur.execute(create_vrednostni_papirji)
    cur.execute(create_transakcije)
    # cur.execute(create_portfelji)
    # cur.execute(create_poker)
    
    conn.commit()

except Exception as error:
    print(error)
finally:
    if cur != None:
        cur.close()
    if conn != None:
        conn.close()