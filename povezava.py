database = 'sem2025_tezakos'
host = 'baza.fmf.uni-lj.si'
port = 5432
user = 'javnost'
password = 'javnogeslo'


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