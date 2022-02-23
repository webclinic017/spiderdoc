import psycopg2,time
from datetime import datetime,timedelta
from datetime import time as tm
import yfinance as yf
import alpaca_trade_api as tradeapi


#con = psycopg2.connect(host='localhost', database='initial_ohlc_db' ,user = 'postgres', password ='Ariel2234')
#curr = con.cursor()

""" list_of_tickers = gt.get_tickers()
print(str(len(list_of_tickers))) """
########## account info ############################
API_ID = 'PKSN7XLSQICEB8BLU4S9'
API_KEY = 'baOGnrJjAeBQfpe8Ql4NHfDwImo45RkkMUt2Vjat'
api_endpoint = 'https://paper-api.alpaca.markets'
####################################################
api = tradeapi.REST(key_id = API_ID,secret_key = API_KEY,base_url = api_endpoint)
print(api.get_account().buying_power)
""" 
curr.execute("delete from dbo.init_ohlc")
con.commit()
curr.execute("delete from dbo.final_ohlc")
con.commit() 

curr.execute('SELECT * FROM dbo.init_ohlc')
rows = curr.fetchall()
for r in rows:
    print(r) """



    

