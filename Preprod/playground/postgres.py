import psycopg2,time
from datetime import datetime,timedelta
import yfinance as yf
from get_all_tickers import get_tickers as gt

con = psycopg2.connect(host='localhost', database='initial_ohlc_db' ,user = 'postgres', password ='Ariel2234')
curr = con.cursor()

""" list_of_tickers = gt.get_tickers()
print(str(len(list_of_tickers))) """
df = yf.download(tickers="NEVDF",period='30m',interval='1m')

print(df)
""" 
curr.execute("delete from dbo.init_ohlc")
con.commit()
curr.execute("delete from dbo.final_ohlc")
con.commit() 

curr.execute('SELECT * FROM dbo.init_ohlc')
rows = curr.fetchall()
for r in rows:
    print(r) """



    

