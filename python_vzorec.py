# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import config


database = config.database
host = config.host
port = config.port
user = config.user
password = config.password

# Ustvarimo povezavo
conn = psycopg2.connect(database=database, host=host, port=port, user=user, password=password)


# Iz povezave naredimo cursor, ki omogoča
# zaganjanje ukazov na bazi

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# Z cur.execute izvedemo SQL ukaz
cur.execute("SELECT * FROM trades")

# Z cur.fetchall() dobimo rezultate
osebe = cur.fetchall()
for oseba in osebe:
    print(oseba)


# Filtriranje z parametri
cur.execute("""
    SELECT * FROM traktor
    WHERE barva = %s
""", ("rdeca",))
for traktor in cur.fetchall():
    print(traktor)

# Zapis novih vrstic (ali pa update)
# Odkomentiraj spodnje vrstice:

# cur.execute("""
#     INSERT INTO oseba (id, ime, rojstvo)
#     VALUES (%s, %s, %s)
# """, (2000, "Janez", "1990-01-01"))

# # Ko naredimo spremembo na bazi, jo moramo potrditi z:
# conn.commit()

# Zapis novih elementov v tabelo s Serial primarnim ključem
# V takih primerih si ponavadi želimo dobiti nazaj generiran ključ!
# To storimo na naslednji način (dodatmo returning id nakoncu):

cur.execute("""
 INSERT INTO traktor (lastnik, znamka, barva, nakup)
    VALUES (%s, %s, %s, %s) returning id
""", (1, 1, 'rdeca' , '2025-01-01'))

# Preberemo generiraj ključ
traktor_id = cur.fetchone()[0]

# Shranimo v bazo
conn.commit()