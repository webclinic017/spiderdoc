from operator import truth
from time import sleep
import pandas as pd
import numpy as np
import yfinance as yf
import multiprocessing
import sys
from datetime import datetime
from datetime import time as tm
import time
import talib
from itertools import compress
import alpaca_trade_api as tradeapi
import gc
import logging

def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    check_time = check_time or datetime.now().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else: # crosses midnight
        return check_time >= begin_time or check_time <= end_time

def stock_amnt_order(close):
    global api
    account = api.get_account()
    balance = account.buying_power
    amount = int(float(balance) / float(close)) -1 
    return amount

def look_for_exit(df,sym,stop_loss,target_price,type,amnt):
    global api
    df = pd.DataFrame()
    while True:
        try:
            #download data
            df = yf.download(tickers=sym,period='3m',interval='1m', progress=False,show_errors=False)
            #remove unfinished candle
            df['Datetime'] = pd.to_datetime(df.index)
            df = df.loc[:,['Datetime', 'Open', 'High', 'Low', 'Close','Volume']]
            logging.info(f'{sym} Downloaded [IN]')
        except :
            logging.warning(f'{sym} Was not Found [IN]')
            continue
            
        curr_minute = datetime.now().minute
        curr_minute -= 1
        
        ts_minutes = df['Datetime'][-1].minute
        if ts_minutes != curr_minute:
            logging.info(f'{sym} Is not to date')
            continue
        else:
            logging.info(f'{sym} Is up to date')
        
        close     = df['Close'][-1]
    
        if type == 'LONG':
            if close > target_price:
                api.close_position(symbol=sym)
                logging.info(f'{sym} LONG target={target_price} close={close} amnt={amnt}')
                logging.info(f' BUY POWER=  {api.get_account().buying_power}')
                logging.info(f'EQUITY={api.get_account().equity}')
                return True
            
            if close < stop_loss:
                api.close_position(symbol=sym)
                logging.info(f'{sym} LONG target={target_price} close={close} amnt={amnt}')
                logging.info(f' BUY POWER=  {api.get_account().buying_power}')
                logging.info(f'EQUITY={api.get_account().equity}')
                return True
        elif type == 'SHORT':
            if close < target_price:
                api.close_position(symbol=sym)
                logging.info(f'{sym} SHORT target={target_price} close={close} amnt={amnt}')
                logging.info(f' BUY POWER=  {api.get_account().buying_power}')
                logging.info(f'EQUITY={api.get_account().equity}')
                return True
            
            if close > stop_loss:
                api.close_position(symbol=sym)
                logging.info(f'{sym} SHORT target={target_price} close={close} amnt={amnt}')
                logging.info(f' BUY POWER=  {api.get_account().buying_power}')
                logging.info(f'EQUITY={api.get_account().equity}')
                return True
        gc.collect()
        time.sleep(10)
                
def main(i):
    
    
    #run alll the time
    global worker_num,api

    ########## account info ############################
    API_ID = 'PKXUYUQ3MW6VTMMHHJFE'
    API_KEY = '5BXvFpDm5uSkJX89JvdBgaZcF10lc2dwSi4Eg5Bu'
    api_endpoint = 'https://paper-api.alpaca.markets'
    ####################################################
    api = tradeapi.REST(key_id = API_ID,secret_key = API_KEY,base_url = api_endpoint)


    while True:
    #this is whre we get out symbols from 
        df = pd.DataFrame()
        file_path = '/input/symbols_'+str(worker_num)+'_'+str(i)+'.txt'
        #file_path = 'C:\DEVOPS\python apps\spiderdoc\spiderdoc\Preprod\Trader\input\symbols_'+str(worker_num)+'_'+str(i)+'.txt'
        Sym_file = open(file_path,"r")
        #apply strategy to all sybols
        start_time = time.time()
        down_fail_c =0
        not_in_time_c = 0
        to_short_c = 0
        for sym in Sym_file:
            sym = sym.strip('\n')
            try:
                #download data
                df = yf.download(tickers=sym,period='70m',interval='1m', progress=False,show_errors=False)
                df = df.resample('1T').interpolate(method='linear', limit_direction='forward', axis=0)
                df['Datetime'] = pd.to_datetime(df.index)
                df = df.loc[:,['Datetime', 'Open', 'High', 'Low', 'Close','Volume']]
                logging.info(f'{sym} Downloaded')
            except :
                logging.info(f'{sym} Was not Found')
                down_fail_c += 1
                continue
            
            #check if sym is up to date
            curr_minute = datetime.now().minute -1
            ts_minutes = df['Datetime'][-1].minute
            
            curr_hour = datetime.now().hour
            ts_hour = df['Datetime'][-1].hour

            if ts_minutes != curr_minute and ts_hour != curr_hour:
                
                ts_minutes = df['Datetime'][-2].minute
                ts_hour = df['Datetime'][-2].hour

                if ts_minutes != curr_minute and ts_hour != curr_hour:
                    not_in_time_c += 1
                    logging.warning(f'{sym} Is not to date')
                    continue
                else:
                    logging.info(f'{sym} Is up to date')
            else:
                logging.info(f'{sym} Is up to date')

            if len(df.index) < 60:
                to_short_c +=1

            try:  
                df['ema60']= talib.SMA(df['Close'].to_numpy(),timeperiod=60)

                df['psar'] = talib.SAR(df['High'].to_numpy(), df['Low'].to_numpy(), acceleration=0.02, maximum=0.2)

                df['macd'],df['macd_signal'],df['macd_hist'] = talib.MACD(df['Close'].to_numpy(), fastperiod=12, slowperiod=26, signalperiod=9)
                            
                df['rsi'] = talib.RSI(df['Close'].to_numpy(), timeperiod=14)
            
                df['adx'] = talib.ADX(df['High'].to_numpy(), df['Low'].to_numpy(), df['Close'].to_numpy(), timeperiod=14)

                df['mdi'] = talib.MINUS_DI(df['High'].to_numpy(),df['Low'].to_numpy(), df['Close'].to_numpy(), timeperiod=14)
                
                df['pdi'] = talib.PLUS_DI(df['High'].to_numpy(),df['Low'].to_numpy(), df['Close'].to_numpy(), timeperiod=14)

                logging.info(f'{sym} Indicators are ready')
            except:
                logging.error(f'{sym} Indicators Failed')
                continue

            #fill trend column
            conditions = [
                (df['ema60'].lt(df['Close'])),
                (df['ema60'].gt(df['Close']))
                        ]    
        
            choices = ['clear_up','clear_down']
            df['trend'] = np.select(conditions, choices, default=0 )

            df = df.loc[:,['Datetime', 'Open', 'High', 'Low', 'Close','Volume','trend','psar','macd_hist','rsi','adx','pdi','mdi','ema60']]

            close     = df['Close'][-1]
            trend     = df['trend'][-1]
            macd_hist = df['macd_hist'][-1]
            psar      = df['psar'][-1]
            rsi       = df['rsi'][-1]
            adx       = df['adx'][-1] 
            pdi       = df['pdi'][-1] 
            mdi       = df['mdi'][-1]

            ema_60 = df['ema60'][-1]
            
            logging.info(f'{sym} Checking Conds') 
            now = datetime.now().time()
            tm0=tm(16,0,0)
            if  now < tm0:  
                logging.debug(f' [CHECK 1 0] {sym} Checking Conds')         
                if trend == 'clear_up':
                    logging.debug(f' [CHECK 1 1] {sym} [LONG] adx= {adx}')
                    if adx > 25 : 
                        logging.debug(f' [CHECK 1 2] {sym} [LONG] macd= {macd_hist}')  
                        if macd_hist > 0:
                            logging.debug(f' [CHECK 1 3] {sym} [LONG] close= {close} psar= {psar}')
                            if close > psar:
                                logging.debug(f' [CHECK 1 4] {sym} [LONG] rsi= {rsi}')
                                if rsi < 50 :
                                    logging.debug(f' [CHECK 1 5] {sym} [LONG] pdi= {pdi} mdi= {mdi}')
                                    if pdi > mdi:
                                        #stop loss at psar
                                        stop_loss = df['psar'][-1] 
                                        # 1:1 with risk rewared
                                        target_price = close + (close- df['psar'][-1])                
                                        stock_amnt = stock_amnt_order(df['Close'][-1])
                                        api.submit_order(symbol=sym,qty=stock_amnt,side='buy',type='market',time_in_force='gtc')
                                        logging.info(f' [ENTER] {sym} [LONG] target= {target_price} stop= {stop_loss} amnt={stock_amnt} close= {close}')
                                        look_for_exit(df,sym,stop_loss,target_price,'LONG',stock_amnt)
                #Short check
                elif trend=='clear_down':
                    logging.debug(f' [CHECK 1 1] {sym} [SHORT] adx= {adx}')
                    if adx > 25 :  
                        logging.debug(f' [CHECK 1 2] {sym} [SHORT] macd= {macd_hist}')  
                        if macd_hist < 0:
                            logging.debug(f' [CHECK 1 3] {sym} [SHORT] close= {close} psar= {psar}')
                            if close < psar:
                                logging.debug(f' [CHECK 1 4] {sym} [SHORT] rsi= {rsi}')
                                if rsi > 50 :
                                    logging.debug(f' [CHECK 1 5] {sym} [SHORT] pdi= {pdi} mdi= {mdi}')
                                    if pdi < mdi:
                                        logging.debug('got here 6')
                                        #stop loss at psar
                                        stop_loss = df['psar'][-1] 
                                        # 1:1 with risk rewared
                                        target_price = close - (df['psar'][-1] - close )                
                                        stock_amnt = stock_amnt_order(df['Close'][-1])
                                        api.submit_order(symbol=sym,qty=stock_amnt,side='sell',type='market',time_in_force='gtc')
                                        logging.info(f' [ENTER] {sym} [SHORT] target= {target_price} stop= {stop_loss} amnt={stock_amnt} close= {close}')
                                        look_for_exit(df,sym,stop_loss,target_price,'SHORT',stock_amnt)
                logging.debug(f' [CHECK 2 1] {sym} [LONG] rsi= {rsi}')
                if rsi < 30:
                    logging.debug(f' [CHECK 2 2] {sym} [LONG] close= {close} psar= {psar}')
                    if psar < close :
                        #stop loss at psar
                        stop_loss = df['psar'][-1] 
                        # 1:1 with risk rewared
                        target_price = close + (close- df['psar'][-1])                
                        stock_amnt = stock_amnt_order(df['Close'][-1])
                        api.submit_order(symbol=sym,qty=stock_amnt,side='buy',type='market',time_in_force='gtc')
                        logging.info(f' [ENTER] {sym} [LONG] target= {target_price} stop= {stop_loss} amnt={stock_amnt} close= {close}')
                        look_for_exit(df,sym,stop_loss,target_price,'LONG',stock_amnt)
                logging.debug(f' [CHECK 2 1] {sym} [SHORT] rsi= {rsi}')
                if rsi > 70:
                    logging.debug(f' [CHECK 2 2] {sym} [SHORT] close= {close} psar= {psar}')
                    if psar > close:
                        #stop loss at psar
                        stop_loss = df['psar'][-1] 
                        # 1:1 with risk rewared
                        target_price = close - (df['psar'][-1] - close )                
                        stock_amnt = stock_amnt_order(df['Close'][-1])
                        api.submit_order(symbol=sym,qty=stock_amnt,side='sell',type='market',time_in_force='gtc')
                        logging.info(f' [ENTER] {sym} [SHORT] target= {target_price} stop= {stop_loss} amnt={stock_amnt} close= {close}')
                        look_for_exit(df,sym,stop_loss,target_price,'SHORT',stock_amnt)
        logging.info(f' [SUMMERY] {worker_num} %s' % (time.time() - start_time)) 
        logging.info(f' [SUMMERY] down_fail_c= {down_fail_c } not_in_time_c= {not_in_time_c} to_short_c= {to_short_c}  -  worker: {worker_num}')
        logging.info(f" [SUMMERY] total fails: {down_fail_c+not_in_time_c+to_short_c}")                                                         


            
            #these values will be put in to a sperate table
        gc.collect()   
        time.sleep(10)
        
global worker_num

""" worker_num = sys.argv[1]
parallel_proc_amnt = sys.argv[2] """

worker_num = sys.argv[1]
parallel_proc_amnt = 32

LOG_FORMAT = '%(asctime)s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG,
filename=f"/log/{datetime.now()}.log",
format=LOG_FORMAT)

if __name__ == '__main__':
    # start n worker processes
    with multiprocessing.Pool(processes=parallel_proc_amnt) as pool:
        pool.map(main,iterable=range(1,parallel_proc_amnt+1))