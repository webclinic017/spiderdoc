import psycopg2,time
con = psycopg2.connect(host='localhost', database='initial_ohlc_db' ,user = 'postgres', password ='Ariel2234')
curr = con.cursor()
curr.execute("select * from dbo.final_ohlc")

rows = curr.fetchall()

for r in rows:
    print(r)
    print (f"id {r[0]} name {r[1]}")

time.sleep(10)

rows = curr.fetchall()

for r in rows:
    print(r)
    print (f"id {r[0]} name {r[1]}")