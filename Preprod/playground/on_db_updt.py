from numpy import lib
import psycopg2
from datetime import datetime as dt
import time
import multiprocessing
import talib
import numpy as np

def get_from_db(symbol):
    
    closes = []
    last_update = 0

    symbol=symbol.strip('\n')

    
    con = psycopg2.connect(host='localhost', database='initial_ohlc_db' ,user = 'postgres', password ='Ariel2234')
    cur = con.cursor()
    while True:
        cur.execute("SELECT timestamp FROM dbo.init_ohlc where symbol = '"+symbol+"' ORDER BY TIMESTAMP DESC LIMIT 1")

        rows = cur.fetchall()

        for r in rows:
            ts = r[0]
            time_obj = dt.strptime(ts, '%Y-%m-%dT%H:%M:%SZ')
            dt.strftime(time_obj, '%y-%m-%d %H:%M:%S%z')
            now = dt.now().minute
            
            if time_obj != last_update:
                cur.execute("SELECT open,close,high,low FROM dbo.init_ohlc where symbol = '"+symbol+"' ORDER BY TIMESTAMP DESC LIMIT 15")
                rows = cur.fetchall()
                for r in rows:
                    close = r[1]
                    closes.append(float(close))
                print(f"closes for {symbol}")
                print(closes)
                last_update = time_obj
                
                
                closes = np.array(closes)

                
                roc_thin = talib.ROCP(closes, timeperiod = 5)
                
                roc_sma_5 = talib.SMA(roc_thin, timeperiod = 5)

                roc_sma_15 = talib.SMA(roc_thin, timeperiod = 15)
                
                rsi = talib.RSI(closes ,timeperiod=14)
                
                #these values will be put in to a sperate table
                roc_delta_15 = roc_sma_15[-1] - roc_sma_15[-2]
                f_roc_sma_5  = roc_sma_5[-1]
                f_roc_sma_15 = roc_sma_15[-1]
                final_rsi    = rsi[-1]
                
                ocpen = rows[0][0]
                close = rows[0][1]
                high  = rows[0][2]
                low   = rows[0][3]
                
                    
            else:
                print(f'not recent for {symbol}')
                time.sleep(10)
        
#file_path = '/input/'+symbols_file
file_path = 'C:\\Users\\nolys\\Desktop\\results\\symbols.txt'
Sym_file = open(file_path,"r")


if __name__ == '__main__':
    # start n worker processes
    with multiprocessing.Pool(processes=3) as pool:
        pool.map_async(get_from_db,iterable=Sym_file).get() 