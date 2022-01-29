from async_timeout import current_task
from numpy import NaN, lib
import psycopg2
from datetime import datetime as dt
import time
import multiprocessing
import talib
import numpy as np
from datetime import datetime,timedelta

def check_for_gaps(timelist):   
    for t in range(1,len(timelist)):
        
        date_t_ob = datetime.strptime(timelist[t], '%Y-%m-%d %H:%M:%S')
        prev_t_ob = datetime.strptime(timelist[t-1], '%Y-%m-%d %H:%M:%S')
        
        one_minute = timedelta(minutes=1)
        new_t_ob = date_t_ob - one_minute
        
        if prev_t_ob != new_t_ob :
            return False
    print('PASSED')
    return True


#open db connection and set cursor
con = psycopg2.connect(host='localhost', database='initial_ohlc_db' ,user = 'postgres', password ='Ariel2234')
cur = con.cursor()
last_update = 0
while True:
    #to make sure we work with the most recent data and to avoid redundency get the last datapoint
    cur.execute("SELECT timestamp FROM dbo.init_ohlc ORDER BY TIMESTAMP DESC LIMIT 1")
    rows = cur.fetchall()
    for r in rows:
        curret_time = r[0]    
    if curret_time != last_update:
        last_update = curret_time
        cur.execute("SELECT symbol FROM dbo.init_ohlc where timestamp = '"+curret_time+"'")
        rows = cur.fetchall()
        #proccess all returned symbols
        for r in rows:
            closes = []
            timestamps = []
            roc_sma_5 = "NaN"
            roc_thin = 'Nan'
            roc_sma_15 = 'NaN'
            rsi = "Nan"
            final_rsi = "NaN"
            copen  = "NaN"
            close  = "NaN"
            high   = "NaN"
            low    = "NaN"
            roc_delta_15 =  "NaN"
            f_roc_sma_5  =  "NaN"
            f_roc_sma_15 =  "NaN"
            final_rsi    =  "NaN"
            
            symbol = r[0]
            print(symbol)
            cur.execute("SELECT open,close,high,low,timestamp FROM dbo.init_ohlc where symbol = '"+symbol+"' ORDER BY timestamp ASC LIMIT 15")
            rows = cur.fetchall()
            for r in rows:
                close = r[1]
                timestamp = r[4]
                closes.append(float(close))
                timestamps.append(timestamp)
            #make sure we have 15 datapoints before proceding
            if len(closes) >= 15 and check_for_gaps(timestamps):
                
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

                cur.execute("insert into dbo.final_ohlc (symbol, timestamp, open, close, high, low, roc_delta_15, roc_sma_5, roc_sma_15, rsi) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                (symbol, curret_time, copen,close, high, low, roc_delta_15, f_roc_sma_5, f_roc_sma_15, final_rsi))
                con.commit()
                
                timestamps = []
                closes = []
    else:
        time.sleep(10)
    
    
    """ if time_obj != last_update:
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
        time.sleep(10) """
