import psycopg2

con = psycopg2.connect(host='localhost', database='initial_ohlc_db' ,user = 'postgres', password ='Ariel2234')
cur = con.cursor()
cur.execute("SELECT timestamp FROM dbo.init_ohlc ORDER BY TIMESTAMP DESC LIMIT 1")

rows = cur.fetchall()

for r in rows:
    print (f"id {r[0]} ")