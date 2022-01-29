import psycopg2,time
from datetime import datetime,timedelta
con = psycopg2.connect(host='localhost', database='initial_ohlc_db' ,user = 'postgres', password ='Ariel2234')
curr = con.cursor()

curr.execute("delete from dbo.init_ohlc")
con.commit()
curr.execute("delete from dbo.final_ohlc")
con.commit() 

curr.execute('SELECT * FROM dbo.init_ohlc')
rows = curr.fetchall()
for r in rows:
    print(r)



    

