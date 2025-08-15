from psycopg2 import sql
from povezava import ustvari_povezavo  # replace with actual module

conn, cur = ustvari_povezavo()

try:
    # Create the trigger function
    create_function = sql.SQL("""
        CREATE OR REPLACE FUNCTION update_portfelji_on_price_insert()
        RETURNS TRIGGER AS $$
        BEGIN
            UPDATE portfelji
            SET vrednost = kolicina * NEW.trenutna_cena
            WHERE simbol = NEW.simbol;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create the trigger
    create_trigger = sql.SQL("""
        CREATE TRIGGER trg_update_portfelji_price_insert
        AFTER INSERT ON delnice
        FOR EACH ROW
        EXECUTE FUNCTION update_portfelji_on_price_insert();
    """)

    # Execute both
    cur.execute(create_function)
    cur.execute(create_trigger)

    conn.commit()
    print("Trigger and function created successfully.")

except Exception as e:
    print(f"Error: {e}")

finally:
    if conn:
        cur.close()
        conn.close()