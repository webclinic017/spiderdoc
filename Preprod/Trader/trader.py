from time import sleep
import pandas as pd
import numpy as np
import yfinance as yf
import multiprocessing
import sys
from datetime import datetime,timedelta
import time
import talib
from itertools import compress
import alpaca_trade_api as tradeapi


#######################################################
    #candle dict
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
        "CDLKICKINGBYLENGTH_Bull": 102,
        "CDLCOUNTERATTACK_Bull" : 102,
        "CDLCOUNTERATTACK_Bear": 102
    }
#######################################################

def get_pattern_df(df):
    global candle_rankings

    # extract OHLC 
    op = df['Open']
    hi = df['High']
    lo = df['Low']
    cl = df['Close']
    
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
    try:
        df['pattern_val']=df['pattern_val'].fillna(0)
    except:
        df['pattern_val']=0
    df.drop(candle_names, axis = 1, inplace = True)
    return df

def stock_amnt_order(close):
    global api
    account = api.get_account()
    balance = account.buying_power
    amount = int(balance / close) -1 
    return amount

def look_for_exit(df,sym):
    while True:
        try:
            #download data
            df = yf.download(tickers=sym,period='30m',interval='1m')
            #remove unfinished candle
            df =df.iloc[0:28,:]
            df['Datetime'] = pd.to_datetime(df.index)
            df = df.loc[:,['Datetime', 'Open', 'High', 'Low', 'Close','Volume']]
            print('FORMATED!')


        except :
            print(f"SYMBOL : {sym} - was not found")
            continue
            
        curr_minute = datetime.now().minute
        curr_minute -= 1
        
        ts_minutes = df['Datetime'][-1].minute
        if ts_minutes != curr_minute:
            continue
        else:
            print(f'Sym : {sym} is up to date')
        
        df =get_pattern_df(df)

        df['roc_thin'] = talib.ROCP(df['Close'], timeperiod = 5)
        
        df['roc_sma_5'] = talib.SMA(df['roc_thin'], timeperiod = 5)

        df['roc_sma_15'] = talib.SMA(df['roc_thin'], timeperiod = 15)
        
        df['rsi'] = talib.RSI(df['Close'] ,timeperiod=14)
        
        df["roc_sma_15_shift"] = df["roc_sma_15"].shift(5)

        df['roc_15_delta'] =df["roc_sma_15"] - df["roc_sma_15_shift"]

        
        df = df.loc[:,['Datetime', 'Open', 'High', 'Low', 'Close','Volume','roc_sma_5','roc_sma_15','pattern_val','candlestick_pattern','roc_15_delta','rsi']]
        if len(api.list_positions())  >= 1:
                roc_5 = df['roc_sma_5'][-1]
                roc_15 = df['roc_sma_15'][-1]
    
                d_roc_15 = df['roc_15_delta'][-1]
    
                if roc_5 <= roc_15 and d_roc_15 < 0:
                    stock_amnt = api.list_positions()[0].qty
                    api.close_position(symbol=sym)
                    print('Exited')
                    return
        time.sleep(10)
            


def main(i):
    
    
    #run alll the time
    global worker_num,candle_names ,api
    candle_names = talib.get_function_groups()['Pattern Recognition']

    ########## account info ############################
    API_ID = 'PKAM4QPHOM4UPBGMF90C'
    API_KEY = '9PdtZ8mifNBGKc8rnVfuZJRMVlFh7shCougkoMal'
    api_endpoint = 'https://paper-api.alpaca.markets'
    ####################################################
    api = tradeapi.REST(key_id = API_ID,secret_key = API_KEY,base_url = api_endpoint)


    while True:
    #this is whre we get out symbols from 
    
        #file_path = '/input/'+symbols_file
        file_path = 'C:\DEVOPS\python apps\spiderdoc\spiderdoc\Preprod\Trader\input\symbols_'+str(worker_num)+'_'+str(i)+'.txt'
        Sym_file = open(file_path,"r")
        #apply strategy to all sybols
        for sym in Sym_file:
            sym = sym.strip('\n')
            try:
                start_time= time.time()
                #download data
                df = yf.download(tickers=sym,period='30m',interval='1m')
                print("########################")
                #remove unfinished candle
                df =df.iloc[0:28,:]
                df['Datetime'] = pd.to_datetime(df.index)
                df = df.loc[:,['Datetime', 'Open', 'High', 'Low', 'Close','Volume']]
                print('FORMATED!')

            except :
                print(f"SYMBOL : {sym} - was not found")
                continue
            
            curr_minute = datetime.now().minute
            curr_minute -= 1
            if len(df) > 0:
                ts_minutes = df['Datetime'][-1].minute
                if ts_minutes != curr_minute:
                    continue
                else:
                    print(f'Sym : {sym} is up to date')
            else:
                continue
            
            df =get_pattern_df(df)

            df['roc_thin'] = talib.ROCP(df['Close'], timeperiod = 5)
            
            df['roc_sma_5'] = talib.SMA(df['roc_thin'], timeperiod = 5)

            df['roc_sma_15'] = talib.SMA(df['roc_thin'], timeperiod = 15)
            
            df['rsi'] = talib.RSI(df['Close'] ,timeperiod=14)
            
            df["roc_sma_15_shift"] = df["roc_sma_15"].shift(5)

            df['roc_15_delta'] =df["roc_sma_15"] - df["roc_sma_15_shift"]

            
            df = df.loc[:,['Datetime', 'Open', 'High', 'Low', 'Close','Volume','roc_sma_5','roc_sma_15','pattern_val','candlestick_pattern','roc_15_delta','rsi']]

        
            d_roc_15 = df['roc_15_delta'][-1]

            if len(api.list_positions())  == 0 and len(api.list_orders()) == 0:                
                if d_roc_15 > 0:
                    if df['roc_sma_5'][-1] > df['roc_sma_15'][-1]:
                        if df['rsi'][-1] < 30:
                            candle_df = get_pattern_df(df)
                            if  '_Bull' in df['candlestick_pattern'][-1]:
                                best_candle_rating=candle_rankings.get(df['candlestick_pattern'][-1],100)
                                candle_rating = df['pattern_val'][-1]
                                if candle_rating > 3 and best_candle_rating < 20:
                                    stock_amnt = stock_amnt_order(df['Close'][-1])
                                    api.submit_order(symbol=sym,qty=stock_amnt,side='buy',type='market',time_in_force='gtc')
                                    print(f"ENTERED for sym : {sym} at time {df['Datetime'][-1]}")
                                    look_for_exit(df,sym)
                                elif candle_rating > 6 and best_candle_rating < 40:
                                    stock_amnt = stock_amnt_order(df['Close'][-1])
                                    api.submit_order(symbol=sym,qty=stock_amnt,side='buy',type='market',time_in_force='gtc')
                                    print(f"ENTERED for sym : {sym} at time {df['Datetime'][-1]}")
                                    look_for_exit(df,sym)
                                elif candle_rating > 7 and best_candle_rating < 60:
                                    stock_amnt = stock_amnt_order(df['Close'][-1])
                                    api.submit_order(symbol=sym,qty=stock_amnt,side='buy',type='market',time_in_force='gtc')
                                    print(f"ENTERED for sym : {sym} at time {df['Datetime'][-1]}")
                                    look_for_exit(df,sym)

            
            #these values will be put in to a sperate table
        time.sleep(10)

global worker_num

""" worker_num = sys.argv[1]
parallel_proc_amnt = sys.argv[2] """

worker_num = 1
parallel_proc_amnt = 1


if __name__ == '__main__':
    # start n worker processes
    with multiprocessing.Pool(processes=parallel_proc_amnt) as pool:
        pool.map_async(main,iterable=range(1,parallel_proc_amnt+1)).get() 