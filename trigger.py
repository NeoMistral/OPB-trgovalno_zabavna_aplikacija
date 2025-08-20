from psycopg2 import sql
from povezava import ustvari_povezavo  

conn, cur = ustvari_povezavo()

try:
    # Drop triggers if they already exist
    cur.execute("DROP TRIGGER IF EXISTS trg_update_portfelji_price_insert ON delnice;")
    cur.execute("DROP TRIGGER IF EXISTS trg_update_vrednost_on_kolicina ON portfelji;")
    cur.execute("DROP TRIGGER IF EXISTS trg_update_vrednost ON portfelji;")

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

    create_trigger_uporabniki = sql.SQL("""
        CREATE TRIGGER trg_update_vrednost
        AFTER INSERT OR UPDATE OR DELETE ON portfelji
        FOR EACH ROW
        EXECUTE FUNCTION update_vrednostni_portfelji();
    """)

    # --- Trigger function + trigger for delnice insert ---
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

    create_trigger_delnice = sql.SQL("""
        CREATE TRIGGER trg_update_portfelji_price_insert
        AFTER INSERT ON delnice
        FOR EACH ROW
        EXECUTE FUNCTION update_portfelji_on_price_insert();
    """)
    
    create_function_portfelji = sql.SQL("""
CREATE OR REPLACE FUNCTION update_vrednost_on_kolicina_change()
RETURNS TRIGGER AS $$
DECLARE
    v_trenutna_cena numeric;
BEGIN
    -- fetch the current price from another table
    SELECT c.trenutna_cena
    INTO v_trenutna_cena
    FROM delnice c
    WHERE c.simbol = NEW.simbol;  -- adjust column to match your relation key

    -- calculate new value
    NEW.vrednost := NEW.kolicina * v_trenutna_cena;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
""")

    # --- Trigger function + trigger for portfelji.kolicina update ---
    # create_function_portfelji = sql.SQL("""
    #     CREATE OR REPLACE FUNCTION update_vrednost_on_kolicina_change()
    #     RETURNS TRIGGER AS $$
    #     BEGIN
    #         NEW.vrednost := NEW.kolicina * trenutna_cena;
    #         RETURN NEW;
    #     END;
    #     $$ LANGUAGE plpgsql;
    # """)

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
