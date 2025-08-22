import baze.config as config

database = config.database
host = config.host
port = config.port
user = config.user
password = config.password

#povezava do baze
def ustvari_povezavo():
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