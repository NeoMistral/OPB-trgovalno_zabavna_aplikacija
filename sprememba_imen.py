import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

import config

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
    
    # spremeni_ime_delnice = """
    # ALTER TABLE delnice
    # RENAME COLUMN id TO vrednostni_papir_id
    # """
    # spremeni_ime_igre = """
    # ALTER TABLE igre
    # RENAME COLUMN id_uporabnika TO uporabnik_id
    # """
    
    # spremeni_ime_arhiv = """
    # ALTER TABLE arhiv
    # RENAME COLUMN id TO vrednostni_papir_id
    # """
    dodaj_stolpce = """
    ALTER TABLE uporabniki
    ADD COLUMN stanje DECIMAL(10, 2) NOT NULL,
    ADD COLUMN vrednostni_portfeljev INTEGER NOT NULL;
    """
    odstrani_uporabnika = """
    DELETE FROM uporabniki WHERE uporabnik_id = 1;
    """
    odstrani_stolpec = """
    ALTER TABLE uporabniki
    DROP COLUMN denarnica_id;    
    """
    
    # cur.execute(spremeni_ime_delnice)
    # cur.execute(spremeni_ime_igre)
    # cur.execute(spremeni_ime_arhiv)
    # cur.execute(odstrani_uporabnika)
    # cur.execute(dodaj_stolpce)
    cur.execute(odstrani_stolpec)
    
    conn.commit()

except Exception as error:
    print(error)
finally:
    if cur != None:
        cur.close()
    if conn != None:
        conn.close()