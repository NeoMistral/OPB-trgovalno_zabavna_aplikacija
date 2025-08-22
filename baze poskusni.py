import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

import config

database = "sem2025_levicbe"
host = "baza.fmf.uni-lj.si"
port = 5432
user = "levicbe"
password = "572z8ijb"
conn = None
cur = None
try:

    conn = psycopg2.connect(
        database="sem2025_levicbe", 
        host=host, 
        port=port, 
        user=user, 
        password=password)

    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    drop_uporabniki = "DROP TABLE IF EXISTS Uporabniki CASCADE;"
    drop_denarnica = "DROP TABLE IF EXISTS Denarnica CASCADE;"
    cur.execute(drop_denarnica)
    cur.execute(drop_uporabniki)

    create_uporabniki = """
    CREATE TABLE IF NOT EXISTS Uporabniki (
        uporabnik_id SERIAL PRIMARY KEY,
        uporabnisko_ime VARCHAR(50) NOT NULL UNIQUE,
        geslo VARCHAR(100) NOT NULL,
        denarnica_id INTEGER NOT NULL,
        FOREIGN KEY (denarnica_id) REFERENCES Denarnica(denarnica_id)
    );
    """
    
    create_denarnica = """
    CREATE TABLE IF NOT EXISTS Denarnica (
        denarnica_id SERIAL PRIMARY KEY,
        vrednostni_portfeljev INTEGER NOT NULL,
        stanje DECIMAL(10, 2) NOT NULL
    );
    """
    
    create_vrednostni_papirji = """
    CREATE TABLE IF NOT EXISTS Vrednostni_papirji (
        vrednostni_papir_id INTEGER PRIMARY KEY,
        market_cap INTEGER NOT NULL,
        cena DECIMAL(10, 2) NOT NULL
    );
    """
    
    create_transakcije = """
    CREATE TABLE IF NOT EXISTS Transakcije (
        transakcija_id SERIAL PRIMARY KEY,
        vrednostni_papir_id INTEGER NOT NULL,
        uporabnik_id INTEGER NOT NULL,
        kolicina INTEGER NOT NULL,
        vrednost DECIMAL(10, 2) NOT NULL,
        datum TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (vrednostni_papir_id) REFERENCES Vrednostni_papirji(vrednostni_papir_id),
        FOREIGN KEY (uporabnik_id) REFERENCES Uporabniki(uporabnik_id)
    );
    """
    
    create_portfelji = """
    CREATE TABLE IF NOT EXISTS Portfelji (
        uporabnik_id INTEGER NOT NULL,
        vrednostni_papir_id INTEGER NOT NULL,
        kolicina INTEGER NOT NULL,
        vrednost DECIMAL(10, 2) NOT NULL,
        PRIMARY KEY (uporabnik_id, vrednostni_papir_id),
        FOREIGN KEY (vrednostni_papir_id) REFERENCES Vrednostni_papirji(vrednostni_papir_id),
        FOREIGN KEY (uporabnik_id) REFERENCES Uporabniki(uporabnik_id)
    );
    """
    
    create_poker = """
    CREATE TABLE IF NOT EXISTS Poker (
        igrana_roka_id SERIAL PRIMARY KEY,
        uporabnik_id INTEGER NOT NULL,
        vložek DECIMAL(10, 2) NOT NULL,
        vrednostni_papir_id INTEGER NOT NULL,
        cas TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        izkupicek DECIMAL(10, 2) NOT NULL,
        FOREIGN KEY (vrednostni_papir_id) REFERENCES Vrednostni_papirji(vrednostni_papir_id),
        FOREIGN KEY (uporabnik_id) REFERENCES Uporabniki(uporabnik_id)
    );
    """
    
    cur.execute(create_denarnica)
    cur.execute(create_vrednostni_papirji)
    cur.execute(create_uporabniki)
    cur.execute(create_transakcije)
    cur.execute(create_portfelji)
    cur.execute(create_poker)

    insert_denarnica = 'INSERT INTO Denarnica (vrednostni_portfeljev, stanje) VALUES (%s, %s);'
    insert_vd = (1, 1000.00)
    
    insert_uporabniki = 'INSERT INTO Uporabniki (uporabnisko_ime, geslo, denarnica_id) VALUES (%s, %s, %s);'
    insert_vu = ('test_user', 'test_password', 1)
    
    cur.execute(insert_denarnica, insert_vd)
    cur.execute(insert_uporabniki, insert_vu)

    
    conn.commit()
    
    cur.execute("SELECT * FROM Denarnica")
    denarnica = cur.fetchall()
    for denarnica_id, vrednosti_portfeljev, stanje, in denarnica:
        print(f"id=denarnica{denarnica_id}, vrednostni_portfeljev={vrednosti_portfeljev}, stanje={stanje}")
        
    
    cur.execute("SELECT * FROM Uporabniki")
    uporabniki = cur.fetchall()
    for uporabnik_id, uporabnisko_ime, geslo, denarnica_id in uporabniki:
        print(f"id=uporabniki{uporabnik_id}, ime={uporabnisko_ime}, geslo={geslo}, denarnica_id={denarnica_id}")

except Exception as error:
    print(error)
finally:
    if cur != None:
        cur.close()
    if conn != None:
        conn.close()