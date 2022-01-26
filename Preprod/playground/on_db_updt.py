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
    print('Starting ...')
    symbol=symbol.strip('\n')

    #open db connection and set cursor
    con = psycopg2.connect(host='localhost', database='initial_ohlc_db' ,user = 'postgres', password ='Ariel2234')
    cur = con.cursor()
    while True:
        #to make sure we work with the most recent data and to avoid redundency get the last datapoint
        cur.execute("SELECT timestamp FROM dbo.init_ohlc where symbol = '"+symbol+"' ORDER BY TIMESTAMP DESC LIMIT 1")
        #featch this data
        rows = cur.fetchall()
        for r in rows:
            ts = r[0]
            #reformat the timestamp
        time_obj = dt.strptime(ts, '%Y-%m-%dT%H:%M:%SZ')
        dt.strftime(time_obj, '%y-%m-%d %H:%M:%S%z')
            #make sure we didnt already process this data
        if time_obj != last_update:
            print(f'new data for symbols {symbol}')
            cur.execute("SELECT open,close,high,low FROM dbo.init_ohlc where symbol = '"+symbol+"' ORDER BY TIMESTAMP DESC LIMIT 30")
            rows = cur.fetchall()
            for r in rows:
                close = r[1]
                closes.append(float(close))
            #set this variable to avoid duplicate processing to avoid redundent data
            last_update = time_obj
            #make sure we have 15 datapoints before proceding
            if len(closes) >= 30:
                
                #tranform list to np array for talib indicators
                closes = np.array(closes)

                #calculate indicators
                roc_thin = talib.ROCP(closes, timeperiod = 5)
                
                roc_sma_5 = talib.SMA(roc_thin, timeperiod = 5)

                roc_sma_15 = talib.SMA(roc_thin, timeperiod = 15)
                
                rsi = talib.RSI(closes ,timeperiod=14)
                
                #these values will be put in to a sperate table
                roc_delta_15 = roc_sma_15[-1] - roc_sma_15[-2]
                f_roc_sma_5  = roc_sma_5[-1]
                f_roc_sma_15 = roc_sma_15[-1]
                final_rsi    = rsi[-1]
                
                #get ohlc from query we already executed
                copen  = rows[0][0]
                close  = rows[0][1]
                high   = rows[0][2]
                low    = rows[0][3]
                print(f"abount to insert to final_ohlc for sym : {symbol}")
                print(f"roc smsa 15: {f_roc_sma_15}")

                cur.execute("insert into dbo.final_ohlc (symbol, timestamp, open, close, high, low, roc_delta_15, roc_sma_5, roc_sma_15, rsi) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                (symbol, time_obj, copen,close, high, low, roc_delta_15, f_roc_sma_5, f_roc_sma_15, final_rsi))
                last_update = time_obj
                con.commit()

            closes = []
               
        else:
            time.sleep(10)
    
#file_path = '/input/'+symbols_file
file_path = 'C:\\DEVOPS\\python apps\\spiderdoc\\spiderdoc\\Preprod\\symbols.txt'

Sym_file = open(file_path,"r")


if __name__ == '__main__':
    # start n worker processes
    with multiprocessing.Pool(processes=20) as pool:
        pool.map_async(get_from_db,iterable=Sym_file).get() 