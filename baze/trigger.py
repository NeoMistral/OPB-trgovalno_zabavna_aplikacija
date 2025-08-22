from psycopg2 import sql
from baze.povezava import ustvari_povezavo  

conn, cur = ustvari_povezavo()

try:
    # Drop triggers if they already exist
    cur.execute("DROP TRIGGER IF EXISTS trg_update_portfelji_price_insert ON delnice;")
    cur.execute("DROP TRIGGER IF EXISTS trg_update_vrednost_on_kolicina ON portfelji;")
    cur.execute("DROP TRIGGER IF EXISTS trg_update_vrednost ON portfelji;")

    # Sums up the total value of all portfolios for a user and updates the user's total portfolio value
    create_function_uporabniki = sql.SQL("""
        CREATE OR REPLACE FUNCTION update_vrednostni_portfelji()
        RETURNS TRIGGER AS $$
        BEGIN
          UPDATE uporabniki u
          SET vrednostni_portfeljev = (
              SELECT COALESCE(SUM(vrednost), 0)
              FROM portfelji
              WHERE uporabnik_id = COALESCE(NEW.uporabnik_id, OLD.uporabnik_id)
          )
          WHERE u.uporabnik_id = COALESCE(NEW.uporabnik_id, OLD.uporabnik_id);

          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    # Trigger to call the function after insert, update, or delete on the "portfelji" table
    create_trigger_uporabniki = sql.SQL("""
        CREATE TRIGGER trg_update_vrednost
        AFTER INSERT OR UPDATE OR DELETE ON portfelji
        FOR EACH ROW
        EXECUTE FUNCTION update_vrednostni_portfelji();
    """)

    # Updates the value of all portfolios when a new stock price is inserted
    create_function_delnice = sql.SQL("""
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

    # Trigger to call the function after insert on the "delnice" table
    create_trigger_delnice = sql.SQL("""
        CREATE TRIGGER trg_update_portfelji_price_insert
        AFTER INSERT ON delnice
        FOR EACH ROW
        EXECUTE FUNCTION update_portfelji_on_price_insert();
    """)
    # Updates the value of a portfolio when its quantity changes 
    create_function_portfelji = sql.SQL("""
        CREATE OR REPLACE FUNCTION update_vrednost_on_kolicina_change()
        RETURNS TRIGGER AS $$
        DECLARE
            v_trenutna_cena numeric;
        BEGIN

        SELECT c.trenutna_cena
        INTO v_trenutna_cena
        FROM delnice c
        WHERE c.simbol = NEW.simbol;

        IF v_trenutna_cena IS NULL THEN
            RAISE EXCEPTION 'No trenutna_cena found for simbol = %', NEW.simbol;
        END IF;

        NEW.vrednost := COALESCE(NEW.kolicina, 0) * v_trenutna_cena;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Trigger to call the function before update of "kolicina" on the "portfelji" table
    create_trigger_portfelji = sql.SQL("""
        CREATE TRIGGER trg_update_vrednost_on_kolicina
        BEFORE UPDATE OF kolicina ON portfelji
        FOR EACH ROW
        EXECUTE FUNCTION update_vrednost_on_kolicina_change();
    """)

    # Execute all statements
    cur.execute(create_function_uporabniki)
    cur.execute(create_trigger_uporabniki)

    cur.execute(create_function_delnice)
    cur.execute(create_trigger_delnice)

    cur.execute(create_function_portfelji)
    cur.execute(create_trigger_portfelji)

    conn.commit()
    print("All triggers and functions created successfully.")

except Exception as e:
    print(f"Error: {e}")

finally:
    if conn:
        cur.close()
        conn.close()
