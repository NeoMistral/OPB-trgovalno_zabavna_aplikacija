import baze.config as config

database = config.database
host = config.host
port = config.port
user = config.user
password = config.password


def ustvari_povezavo():
    """
    Creates and returns a connection and cursor to the PostgreSQL database.
    
    Returns:
        conn: Connection object to the PostgreSQL database.
        cur: Cursor object for executing SQL commands.
    """
    import psycopg2
    conn = psycopg2.connect(
        host=host,
        database=database,  
        user=user,  
        password=password,
        port = port 
    )
    cur = conn.cursor() 
    return conn, cur