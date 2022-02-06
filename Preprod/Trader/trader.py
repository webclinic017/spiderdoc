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


def stock_amnt_order(close):
    global api
    account = api.get_account()
    balance = account.buying_power
    amount = int(balance / close) -1 
    return amount

def look_for_exit(df,sym,stop_loss,target_price,type):
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
        
        close     = df['Close'][-1]
    
        if type == 'LONG':
            if close > target_price:
                print('TARGET REACHED')
                return True
            
            if close < stop_loss:
                print('STOP LOSS')
                return True
        elif type == 'SHORT':
            if close < target_price:
                print('TARGET REACHED')
                return True
            
            if close > stop_loss:
                print('STOP LOSS')
                return True
    
        time.sleep(10)
                
def main(i):
    
    
    #run alll the time
    global worker_num,candle_names ,api
    candle_names = talib.get_function_groups()['Pattern Recognition']

    ########## account info ############################
    API_ID = 'PKLQW1C4WIB6XI2LOQ5W'
    API_KEY = 'ohdklwFBMMMHbnpIjrUplgpYupnl7viaFofhbgyd'
    api_endpoint = 'https://paper-api.alpaca.markets'
    ####################################################
    api = tradeapi.REST(key_id = API_ID,secret_key = API_KEY,base_url = api_endpoint)


    while True:
    #this is whre we get out symbols from 
    
        file_path = '/input/symbols_'+str(worker_num)+'_'+str(i)+'.txt'
        #file_path = 'C:\DEVOPS\python apps\spiderdoc\spiderdoc\Preprod\Trader\input\symbols_'+str(worker_num)+'_'+str(i)+'.txt'
        Sym_file = open(file_path,"r")
        #apply strategy to all sybols
        start_time = time.time()
        for sym in Sym_file:
            sym = sym.strip('\n')
            try:
                #download data
                df = yf.download(tickers=sym,period='70m',interval='1m')
                #remove unfinished candle
                df =df.iloc[0:28,:]
                df['Datetime'] = pd.to_datetime(df.index)
                df = df.loc[:,['Datetime', 'Open', 'High', 'Low', 'Close','Volume']]
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
            try:  
                df['ema60']= talib.SMA(df['Close'].to_numpy(),timeperiod=60)

                df['psar'] = talib.SAR(df['High'].to_numpy(), df['Low'].to_numpy(), acceleration=0.02, maximum=0.2)

                df['macd'],df['macd_signal'],df['macd_hist'] = talib.MACD(df['Close'].to_numpy(), fastperiod=12, slowperiod=26, signalperiod=9)
                            
                df['rsi'] = talib.RSI(df['Close'].to_numpy(), timeperiod=14)
            
                df['adx'] = talib.ADX(df['High'].to_numpy(), df['Low'].to_numpy(), df['Close'].to_numpy(), timeperiod=14)

                df['mdi'] = talib.MINUS_DI(df['High'].to_numpy(),df['Low'].to_numpy(), df['Close'].to_numpy(), timeperiod=14)
                
                df['pdi'] = talib.PLUS_DI(df['High'].to_numpy(),df['Low'].to_numpy(), df['Close'].to_numpy(), timeperiod=14)
            except:
                print('failed to calc metrics')
                continue

            #fill trend column
            conditions = [
                (df['ema60'].lt(df['Close'])),
                (df['ema60'].gt(df['Close']))
                        ]    
        
            choices = ['clear_up','clear_down']
            df['trend'] = np.select(conditions, choices, default=0 )

            df = df.loc[:,['Datetime', 'Open', 'High', 'Low', 'Close','Volume','trend','psar','macd_hist','rsi','adx','pdi','mdi']]

            close     = df['Close'][-1]
            trend     = df['trend'][-1]
            macd_hist = df['macd_hist'][-1]
            psar      = df['psar'][-1]
            rsi       = df['rsi'][-1]
            adx       = df['adx'][i] 
            pdi       = df['pdi'][i] 
            mdi       = df['mdi'][i]
            
            print('ALL METERICS CALLED')
            #check aroon is not parallel and not in 100 / 0 (up or down)   

            if len(api.list_positions())  == 0 and len(api.list_orders()) == 0:                
                if trend == 'clear_up':
                    if adx > 25 :   
                        if macd_hist > 0:
                            if close > psar:
                                if rsi < 50 :
                                    if pdi > mdi:
                                        #stop loss at psar
                                        stop_loss = df['psar'][-1] 
                                        # 1:1 with risk rewared
                                        target_price = close + (close- df['psar'][-1])                
                                        stock_amnt = stock_amnt_order(df['Close'][-1])
                                        api.submit_order(symbol=sym,qty=stock_amnt,side='buy',type='market',time_in_force='gtc')
                                        print("ENTERED ++++++++++++++")
                                        look_for_exit(df,sym,stop_loss,target_price,'LONG')
                                        print("EXITED ===============")
                #Short check
                elif trend=='clear_down':
                    if adx > 25 :   
                        if macd_hist < 0:
                            if close < psar:
                                if rsi > 50 :
                                    if pdi < mdi:
                                        #stop loss at psar
                                        stop_loss = df['psar'][-1] 
                                        # 1:1 with risk rewared
                                        target_price = close - (df['psar'][-1] - close )                
                                        stock_amnt = stock_amnt_order(df['Close'][-1])
                                        api.submit_order(symbol=sym,qty=stock_amnt,side='sell',type='market',time_in_force='gtc')
                                        print("ENTERED ++++++++++++++")
                                        look_for_exit(df,sym,stop_loss,target_price,'short')
                                        print("EXITED ===============")

        print("--- %s seconds ---" % (time.time() - start_time))                                                           


            
            #these values will be put in to a sperate table
        time.sleep(100)

global worker_num

""" worker_num = sys.argv[1]
parallel_proc_amnt = sys.argv[2] """

worker_num = 1
parallel_proc_amnt = 16


if __name__ == '__main__':
    # start n worker processes
    with multiprocessing.Pool(processes=parallel_proc_amnt) as pool:
        pool.map_async(main,iterable=range(1,parallel_proc_amnt+1)).get() 