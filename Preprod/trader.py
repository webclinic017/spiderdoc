from numpy import lib
import pandas as pd
import psycopg2
from datetime import datetime as dt
import time
import multiprocessing
import alpaca_trade_api as tradeapi
import numpy as np
from itertools import compress
import talib

global candle_rankings

candle_rankings = {
        "CDL3LINESTRIKE_Bull": 1,
        "CDL3LINESTRIKE_Bear": 2,
        "CDL3BLACKCROWS_Bull": 3,
        "CDL3BLACKCROWS_Bear": 3,
        "CDLEVENINGSTAR_Bull": 4,
        "CDLEVENINGSTAR_Bear": 4,
        "CDLTASUKIGAP_Bull": 5,
        "CDLTASUKIGAP_Bear": 5,
        "CDLINVERTEDHAMMER_Bull": 6,
        "CDLINVERTEDHAMMER_Bear": 6,
        "CDLMATCHINGLOW_Bull": 7,
        "CDLMATCHINGLOW_Bear": 7,
        "CDLABANDONEDBABY_Bull": 8,
        "CDLABANDONEDBABY_Bear": 8,
        "CDLBREAKAWAY_Bull": 10,
        "CDLBREAKAWAY_Bear": 10,
        "CDLMORNINGSTAR_Bull": 12,
        "CDLMORNINGSTAR_Bear": 12,
        "CDLPIERCING_Bull": 13,
        "CDLPIERCING_Bear": 13,
        "CDLSTICKSANDWICH_Bull": 14,
        "CDLSTICKSANDWICH_Bear": 14,
        "CDLTHRUSTING_Bull": 15,
        "CDLTHRUSTING_Bear": 15,
        "CDLINNECK_Bull": 17,
        "CDLINNECK_Bear": 17,
        "CDL3INSIDE_Bull": 20,
        "CDL3INSIDE_Bear": 56,
        "CDLHOMINGPIGEON_Bull": 21,
        "CDLHOMINGPIGEON_Bear": 21,
        "CDLDARKCLOUDCOVER_Bull": 22,
        "CDLDARKCLOUDCOVER_Bear": 22,
        "CDLIDENTICAL3CROWS_Bull": 24,
        "CDLIDENTICAL3CROWS_Bear": 24,
        "CDLMORNINGDOJISTAR_Bull": 25,
        "CDLMORNINGDOJISTAR_Bear": 25,
        "CDLXSIDEGAP3METHODS_Bull": 27,
        "CDLXSIDEGAP3METHODS_Bear": 26,
        "CDLTRISTAR_Bull": 28,
        "CDLTRISTAR_Bear": 76,
        "CDLGAPSIDESIDEWHITE_Bull": 46,
        "CDLGAPSIDESIDEWHITE_Bear": 29,
        "CDLEVENINGDOJISTAR_Bull": 30,
        "CDLEVENINGDOJISTAR_Bear": 30,
        "CDL3WHITESOLDIERS_Bull": 32,
        "CDL3WHITESOLDIERS_Bear": 32,
        "CDLONNECK_Bull": 33,
        "CDLONNECK_Bear": 33,
        "CDL3OUTSIDE_Bull": 34,
        "CDL3OUTSIDE_Bear": 39,
        "CDLRICKSHAWMAN_Bull": 35,
        "CDLRICKSHAWMAN_Bear": 35,
        "CDLSEPARATINGLINES_Bull": 36,
        "CDLSEPARATINGLINES_Bear": 40,
        "CDLLONGLEGGEDDOJI_Bull": 37,
        "CDLLONGLEGGEDDOJI_Bear": 37,
        "CDLHARAMI_Bull": 38,
        "CDLHARAMI_Bear": 72,
        "CDLLADDERBOTTOM_Bull": 41,
        "CDLLADDERBOTTOM_Bear": 41,
        "CDLCLOSINGMARUBOZU_Bull": 70,
        "CDLCLOSINGMARUBOZU_Bear": 43,
        "CDLTAKURI_Bull": 47,
        "CDLTAKURI_Bear": 47,
        "CDLDOJISTAR_Bull": 49,
        "CDLDOJISTAR_Bear": 51,
        "CDLHARAMICROSS_Bull": 50,
        "CDLHARAMICROSS_Bear": 80,
        "CDLADVANCEBLOCK_Bull": 54,
        "CDLADVANCEBLOCK_Bear": 54,
        "CDLSHOOTINGSTAR_Bull": 55,
        "CDLSHOOTINGSTAR_Bear": 55,
        "CDLMARUBOZU_Bull": 71,
        "CDLMARUBOZU_Bear": 57,
        "CDLUNIQUE3RIVER_Bull": 60,
        "CDLUNIQUE3RIVER_Bear": 60,
        "CDL2CROWS_Bull": 61,
        "CDL2CROWS_Bear": 61,
        "CDLBELTHOLD_Bull": 62,
        "CDLBELTHOLD_Bear": 63,
        "CDLHAMMER_Bull": 65,
        "CDLHAMMER_Bear": 65,
        "CDLHIGHWAVE_Bull": 67,
        "CDLHIGHWAVE_Bear": 67,
        "CDLSPINNINGTOP_Bull": 69,
        "CDLSPINNINGTOP_Bear": 73,
        "CDLUPSIDEGAP2CROWS_Bull": 74,
        "CDLUPSIDEGAP2CROWS_Bear": 74,
        "CDLGRAVESTONEDOJI_Bull": 77,
        "CDLGRAVESTONEDOJI_Bear": 77,
        "CDLHIKKAKEMOD_Bull": 82,
        "CDLHIKKAKEMOD_Bear": 81,
        "CDLHIKKAKE_Bull": 85,
        "CDLHIKKAKE_Bear": 83,
        "CDLENGULFING_Bull": 84,
        "CDLENGULFING_Bear": 91,
        "CDLMATHOLD_Bull": 86,
        "CDLMATHOLD_Bear": 86,
        "CDLHANGINGMAN_Bull": 87,
        "CDLHANGINGMAN_Bear": 87,
        "CDLRISEFALL3METHODS_Bull": 94,
        "CDLRISEFALL3METHODS_Bear": 89,
        "CDLKICKING_Bull": 96,
        "CDLKICKING_Bear": 102,
        "CDLDRAGONFLYDOJI_Bull": 98,
        "CDLDRAGONFLYDOJI_Bear": 98,
        "CDLCONCEALBABYSWALL_Bull": 101,
        "CDLCONCEALBABYSWALL_Bear": 101,
        "CDL3STARSINSOUTH_Bull": 103,
        "CDL3STARSINSOUTH_Bear": 103,
        "CDLDOJI_Bull": 104,
        "CDLDOJI_Bear": 104 ,
        "CDLLONGLINE_Bull": 53,
        "CDLLONGLINE_Bear": 53,
        "CDLSHORTLINE_Bull": 85,
        "CDLSHORTLINE_Bear": 66,
        "CDLSTALLEDPATTERN_Bull": 93,
        "CDLSTALLEDPATTERN_Bear": 93,
        "CDLKICKINGBYLENGTH": 96,
        "CDLKICKINGBYLENGTH_Bear": 102,
        "CDLCOUNTERATTACK_Bull" : 102,
        "CDLCOUNTERATTACK_Bear": 102
    }


def get_from_db(symbol):
    global df,api
    
    timestamps  = []
    closes      = []
    opens       = []
    highs       = []
    lows        = []
    rsis        = []
    roc_5s      = []
    roc_15s     = []
    last_update = 0

    symbol=symbol.strip('\n')

    #open db connection and set cursor
    con = psycopg2.connect(host='localhost', database='initial_ohlc_db' ,user = 'postgres', password ='Ariel2234')
    cur = con.cursor()
    
    ########## account info ############################
    API_ID = 'PKAM4QPHOM4UPBGMF90C'
    API_KEY = '9PdtZ8mifNBGKc8rnVfuZJRMVlFh7shCougkoMal'
    api_endpoint = 'https://paper-api.alpaca.markets'
    ####################################################
    api = tradeapi.REST(key_id = API_ID,secret_key = API_KEY,base_url = api_endpoint)

    
    while True:
        #to make sure we work with the most recent data and to avoid redundency get the last datapoint
        cur.execute("SELECT timestamp FROM dbo.final_ohlc where symbol = '"+symbol+"' ORDER BY TIMESTAMP DESC LIMIT 1")
        #featch this data
        rows = cur.fetchall()

        for r in rows:
            ts = r[0]
            #reformat the timestamp
        time_obj = dt.strptime(ts, '%Y-%m-%d %H:%M:%S')
            #make sure we didnt already process this data
        if time_obj != last_update:
            #make sure we didnt already process this data
            last_update = time_obj
            
            #run query to get the most recent data
            cur.execute("SELECT timestamp, open, close, high, low, rsi,roc_sma_5, roc_sma_15 FROM dbo.final_ohlc where symbol = '"+symbol+"' ORDER BY TIMESTAMP DESC LIMIT 1 ")
            rows = cur.fetchall()
            
            #truncates thr list that make up the df if over a threhold
            max_len = 59
            if len(timestamps) >= max_len:
                cut_from = len(timestamps) - max_len 
                timestamps  = timestamps  [cut_from:]
                opens       = opens       [cut_from:]
                closes      = closes      [cut_from:]
                highs       = highs       [cut_from:]
                lows        = lows        [cut_from:]
                rsis        = rsis        [cut_from:]
                roc_15s     = roc_15s     [cut_from:]
                roc_5s      = roc_5s      [cut_from:]
            
            #append data form query to the list 
            for r in rows:
                timestamp = r[0]
                copen     = r[1]
                close     = r[2]
                high      = r[3]
                low       = r[4]
                rsi       = r[5]
                roc_5     = r[6]
                roc_15    = r[7]
                
                timestamps.append(timestamp)
                opens.append(copen)
                closes.append(close)
                highs.append(high)
                lows.append(low)
                rsis.append(rsi)
                roc_5s.append(roc_5)
                roc_15s.append(roc_15)
            
            #build a dataframe from lists    
            df = pd.DataFrame()
            df['Timestamp'] = timestamps
            df['Open']      = opens
            df['Low']       = lows
            df['High']      = highs
            df['Close']     = closes
            df['RSI']       = rsis
            df['roc_5']     = roc_5s
            df['roc_15']    = roc_15s                
            
        if df['Timestamp'][-1] == 'NaN':
            continue
        if df['Open'][-1] == 'NaN':
            continue
        if df['Low'][-1] == 'NaN':
            continue
        if df['High'][-1] == 'NaN':
            continue
        if df['Close'][-1] == 'NaN':
            continue
        if df['RSI'][-1] == 'NaN':
            continue
        if df['roc_5'][-1] == 'NaN':
            continue
        if df['roc_15'][-1] == 'NaN':
            continue
        
                        #STRATEGY
        ######################################################################
        #   when rsi dips bellow 30 check for strong bull signals with roc5 > roc 15 - BUY BUY BUY
        #   when roc5 dips bellow roc 15 - SELL SELL SELL                           
        if len(api.list_positions())  == 0 and len(api.list_orders()) == 0:                
            if roc_5 > roc_15:
                if df['rsi'][-1] < 30:
                    candle_df = get_pattern_df(df)
                    if  '_Bull' in candle_df['candlestick_pattern'][-1]:
                        best_candle_rating=candle_rankings.get(candle_df['candlestick_pattern'][-1],100)
                        candle_rating = df['pattern_val'][-1]
                        if candle_rating > 3 and best_candle_rating < 20:
                            stock_amnt = stock_amnt_order(closes[-1])
                            api.submit_order(symbol=symbol,qty=stock_amnt,side='buy',type='market',time_in_force='gtc')
                        elif candle_rating > 6 and best_candle_rating < 40:
                            stock_amnt = stock_amnt_order(closes[-1])
                            api.submit_order(symbol=symbol,qty=stock_amnt,side='buy',type='market',time_in_force='gtc')
                        elif candle_rating > 7 and best_candle_rating < 60:
                            stock_amnt = stock_amnt_order(closes[-1])
                            api.submit_order(symbol=symbol,qty=stock_amnt,side='buy',type='market',time_in_force='gtc')
        elif len(api.list_positions())  >= 1:
            roc_5 = df['roc_sma_5'][-1]
            
            roc_15 = df['roc_sma_15'][-1]
            
            roc_roc_5 = df["roc_roc_5"][-1]
            
            if roc_5 <= roc_15:
                stock_amnt = api.list_positions()[1].qty
                api.submit_order(symbol=symbol,qty=stock_amnt,side='sell',type='market',time_in_force='gtc',order_class='bracket')
            
            
                
        else :
            time.sleep(10)        

def get_pattern_df(df):
    global candle_rankings

    
    # extract OHLC 
    op = df['Open']
    hi = df['High']
    lo = df['Low']
    cl = df['Close']
    
    candle_names = talib.get_function_groups()['Pattern Recognition']
    # create columns for each pattern
    for candle in candle_names:
        # below is same as;
        # df["CDL3LINESTRIKE"] = talib.CDL3LINESTRIKE(op, hi, lo, cl)
        df[candle] = getattr(talib, candle)(op, hi, lo, cl)
        
        #reduce helper cols in to one col
        
    df['candlestick_pattern'] = np.nan
    df['candlestick_match_count'] = np.nan
    for index, row in df.iterrows():

        # no pattern found
        if len(row[candle_names]) - sum(row[candle_names] == 0) == 0:
            df.loc[index,'candlestick_pattern'] = "NO_PATTERN"
            df.loc[index, 'candlestick_match_count'] = 0
        # single pattern found
        elif len(row[candle_names]) - sum(row[candle_names] == 0) == 1:
            # bull pattern 100 or 200
            if any(row[candle_names].values > 0):
                pattern = list(compress(row[candle_names].keys(), row[candle_names].values != 0))[0] + '_Bull'
                df.loc[index, 'candlestick_pattern'] = pattern
                df.loc[index, 'candlestick_match_count'] = 1
            # bear pattern -100 or -200
            else:
                pattern = list(compress(row[candle_names].keys(), row[candle_names].values != 0))[0] + '_Bear'
                df.loc[index, 'candlestick_pattern'] = pattern
                df.loc[index, 'candlestick_match_count'] = 1
        # multiple patterns matched -- select best performance
        else:
            # filter out pattern names from bool list of values
            patterns = list(compress(row[candle_names].keys(), row[candle_names].values != 0))
            container = []
            container_val = 0
            for pattern in patterns:
                if row[pattern] > 0:
                    container.append(pattern + '_Bull')
                    container_val += 1
                else:
                    container.append(pattern + '_Bear')
                    container_val -= 1
            rank_list = [candle_rankings[p] for p in container]
            if len(rank_list) == len(container):
                rank_index_best = rank_list.index(min(rank_list))
                df.loc[index, 'candlestick_pattern'] = container[rank_index_best]
                df.loc[index, 'pattern_val'] = container_val
                df.loc[index, 'candlestick_match_count'] = len(container)
    # clean up candle columns
    df['pattern_val']=df['pattern_val'].fillna(0)
    df.drop(candle_names, axis = 1, inplace = True)
    return df         


def stock_amnt_order(close):
    global api
    account = api.get_account()
    balance = account.buying_power
    amount = int(balance / close) -1 
    return amount



file_path = 'C:\\DEVOPS\\python apps\\spiderdoc\\spiderdoc\\Preprod\\symbols.txt'
Sym_file = open(file_path,"r")


if __name__ == '__main__':
    # start n worker processes
    with multiprocessing.Pool(processes=20) as pool:
        pool.map_async(get_from_db,iterable=Sym_file).get()                