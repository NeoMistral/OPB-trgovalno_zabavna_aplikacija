from povezava import ustvari_povezavo

def update_transakcije_table():
    conn, cur = ustvari_povezavo()

    try:
        # First change column type
        alter_type_query = """
            ALTER TABLE transakcije
            ALTER COLUMN vrednostni_papir_id TYPE varchar(10);
        """
        cur.execute(alter_type_query)

        # Then rename the column
        rename_column_query = """
            ALTER TABLE transakcije
            RENAME COLUMN vrednostni_papir_id TO simbol;
        """
        cur.execute(rename_column_query)

        conn.commit()
        print("Table 'transakcije' updated successfully.")
    except Exception as e:
        print(f"Error updating table: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()
