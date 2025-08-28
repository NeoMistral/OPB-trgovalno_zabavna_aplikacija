import os
import configparser

# Path to config file
config_file = os.path.join(os.path.dirname(__file__), 'baza.config')
config = configparser.ConfigParser()
config.read(config_file)

database = config.get('DATABASE', 'database')
host = config.get('DATABASE', 'host')
port = config.get('DATABASE', 'port')
user = config.get('DATABASE', 'user')
password = config.get('DATABASE', 'password')

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