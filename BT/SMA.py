#imports
from ntpath import join
import os
import alpaca_trade_api as tradeapi
import ta
import pandas as pd
import matplotlib.pyplot as plt 
import numpy as np 
import yfinance as yf
from datetime import timedelta,time,datetime
import sys
import multiprocessing

get_rid_of_position = False
position_is_open=False
symbols_file = sys.argv[1]
start_date_range = sys.argv[2]
end_date_range = sys.argv[3]
run_type = sys.argv[4]
prallel_proc_amnt = sys.argv[5]
prallel_proc_amnt=int(prallel_proc_amnt)

positions              = pd.DataFrame(columns=['Timestamp','Action','Amount','Price','TValue','Intent','Balance'])
#for eval 
positions_short        = pd.DataFrame(columns=['Action','Price','Amount','TValue','Intent'])
positions_closed_short = pd.DataFrame(columns=['Action','Price','Amount','TValue','Intent'])
positions_long         = pd.DataFrame(columns=['Action','Price','Amount','TValue','Intent'])
positions_closed_longs = pd.DataFrame(columns=['Action','Price','Amount','TValue','Intent'])
positions.set_index('Timestamp')
#assign before referance

########################################################################################################################
#                                           FUNCTIONS
########################################################################################################################

def update_pos(index,action,price,amount,tvalue,intent,balance) :
    global positions
    positions.loc[index,'Action']=action
    positions.loc[index,'Amount']=amount
    positions.loc[index,'Price']=price
    positions.loc[index,'TValue']=tvalue
    positions.loc[index,'Intent']=intent
    positions.loc[index,'Balance']=balance

def update_pos_long(index,action,amount,price,tvalue,intent) :
    positions_long .loc[index,'Action']=action
    positions_long.loc[index,'Amount']=amount
    positions_long.loc[index,'Price']=price
    positions_long.loc[index,'TValue']=tvalue
    positions_long.loc[index,'Intent']=intent
    
def update_pos_closed_long(index,action,amount,price,tvalue,intent) :
    positions_closed_longs.loc[index,'Action']=action
    positions_closed_longs.loc[index,'Amount']=amount
    positions_closed_longs.loc[index,'Price']=price
    positions_closed_longs.loc[index,'TValue']=tvalue
    positions_closed_longs.loc[index,'Intent']=intent
    
def update_pos_short(index,action,amount,price,tvalue,intent) :
    positions.loc[index,'Action']=action
    positions_short.loc[index,'Amount']=amount
    positions_short.loc[index,'Price']=price
    positions_short.loc[index,'TValue']=tvalue
    positions_short.loc[index,'Intent']=intent
    
def update_pos_closed_short(index,action,amount,price,tvalue,intent) :
    positions_closed_short.loc[index,'Action']=action
    positions_closed_short.loc[index,'Amount']=amount
    positions_closed_short.loc[index,'Price']=price
    positions_closed_short.loc[index,'TValue']=tvalue
    positions_closed_short.loc[index,'Intent']=intent

def update_balance (balance,trans_value,action,intent):
    if (action == "buy" and intent=="LONG") or (action == "sell" and intent == "SHORT") :
        balance = balance - trans_value
    else:
        balance = balance + trans_value
    return balance

def update_stock_amnt (balance,stock_price):
    tmp_mod=balance % stock_price
    tmp_balace=balance-tmp_mod
    stock_amnt=tmp_balace / stock_price
    return stock_amnt

def run_simulation(stock_to_trade):
    get_rid_of_position = False
    position_is_open=False
    stock_not_avail = False
    global start_date_range 
    global end_date_range 
    global run_type 
    stock_to_trade=stock_to_trade.strip('\n')
   
    a = datetime.strptime(start_date_range, "%Y-%m-%d")
    b = datetime.strptime(end_date_range, "%Y-%m-%d")
    delta_date = b - a
    #initialize position dataframe with null's ans 0's
    curr_date = start_date_range
    curr_date = datetime. strptime(curr_date, '%Y-%m-%d')
    curr_date=curr_date - timedelta(days=1) 
    balance = 10000

    for day in range(delta_date.days):
    #########################################################################################################################
    #                                           New Day initilazion
    #                                           ==================
    #########################################################################################################################                                            
        global positions
        positions              = pd.DataFrame(columns=['Timestamp','Action','Amount','Price','TValue','Intent'])
        #for eval 
        positions_short        = pd.DataFrame(columns=['Action','Price','Amount','TValue','Intent'])
        positions_closed_short = pd.DataFrame(columns=['Action','Price','Amount','TValue','Intent'])
        positions_long         = pd.DataFrame(columns=['Action','Price','Amount','TValue','Intent'])
        positions_closed_longs = pd.DataFrame(columns=['Action','Price','Amount','TValue','Intent'])
        curr_date=curr_date + timedelta(days=1) 
        update_pos('0000-00-00 00:00:00-00:00','NA',0,0,0,'NA',balance)
        if run_type != 'REAL' :
            balance=10000
        tommorow_date =curr_date + timedelta(days=1)
        get_rid_of_position = False 
        #skips loop run if staurday
        if curr_date.weekday() == 5 or curr_date.weekday() == 6 :
            continue
        ########################################################################################################################
        #                                      Data and Metrics for this day are calculated Here
        #                                     ===================================================
        ########################################################################################################################
        #get historical data from yfinance for this day
        try:
            curr_stock_historical = yf.download(stock_to_trade,curr_date,tommorow_date,interval='1m')
            curr_stock_historical.head()
        except:
            stock_not_avail = True
            break
        #calaculate SMA of 15 minutes for this day
        curr_stock_historical['SMA']= ta.trend.sma_indicator(curr_stock_historical['Close'],window=15,fillna=True)
        #current price reletive to SMA this day
        close_relto_sma=curr_stock_historical['Close']-curr_stock_historical['SMA']
        #cast into pandas df
        curr_stock_historical_close=pd.DataFrame(curr_stock_historical['Close'])
        curr_stock_historical_close.reindex()
        #5min rolling sum of Close to SMA
        RS5m_close_relto_sma=pd.DataFrame(close_relto_sma,columns=['CRS'])
        RS5m_close_relto_sma.rolling(5).sum()

        #set stock amount to be traded
        stock_amnt=1000
        ########################################################################################################################
                                                    #STRATEGY#
                                                    #========#
        ########################################################################################################################
        for index, row in curr_stock_historical['Close'].iteritems():
            prev_index = index - timedelta(minutes=1)
            current_time = time(index.hour, index.minute, index.second)
            
            #set when to stop opening positions 
            close_time = time(hour=15,minute=30,second=00)
            
            #what was the intent of the previos trade in positions
            last_intent = positions.iloc[-1]['Intent']

            #checks if its closing time       
            if(close_time<current_time):
                get_rid_of_position = True
            
            #if the difference between close and SMA is negetive its bellow SMA ,when higher then 0 its above
            above_sma =close_relto_sma.loc[index] > 0
            avg_above_sma =RS5m_close_relto_sma['CRS']> 0
            curr_price =curr_stock_historical.loc[index]['Close']
            stock_amnt=update_stock_amnt(balance,curr_price)
            #true when stock price is above SMA
            if(above_sma):
                #no open positions and its not closing time - BUY LONG
                if(position_is_open == False and get_rid_of_position==False and avg_above_sma.loc[index]==True ):
                    position_is_open=True
                    action='buy'
                    intent = 'LONG'
                    curr_price =curr_stock_historical.loc[index]['Close']
                    stock_amnt=update_stock_amnt(balance,curr_price)
                    trans_value=curr_price*stock_amnt
                    if run_type == 'ADJ' or 'REAL' :
                        balance=update_balance(balance,trans_value,action,intent)
                    update_pos(index,action,curr_price,stock_amnt,trans_value,intent,balance)    
                #open position with a short intent = CLOSE SHORT
                elif(position_is_open == True and last_intent=="SHORT"):
                    position_is_open=False
                    action='buy'
                    intent = 'CLOSE_SHORT'
                    curr_price =curr_stock_historical.loc[index]['SMA']
                    stock_amnt =positions.iloc[-1]['Amount']
                    trans_value=curr_price*stock_amnt
                    if run_type == 'ADJ' or 'REAL' :
                        balance=update_balance(balance,trans_value,action,intent)
                    update_pos(index,action,curr_price,stock_amnt,trans_value,intent,balance)    
            elif( above_sma==False):
                if(position_is_open == True and last_intent=="LONG"):
                    position_is_open=False
                    action='sell'
                    intent = 'CLOSE_LONG'
                    curr_price =curr_stock_historical.loc[index]['SMA']
                    stock_amnt=positions.iloc[-1]['Amount']
                    trans_value=curr_price*stock_amnt
                    if run_type == 'ADJ' or 'REAL' :
                        balance=update_balance(balance,trans_value,action,intent)
                    update_pos(index,action,curr_price,stock_amnt,trans_value,intent,balance)    
                        
                elif(position_is_open == False and get_rid_of_position==False and avg_above_sma.loc[index] == False):
                    position_is_open=True
                    action='sell'
                    intent = 'SHORT'
                    curr_price =curr_stock_historical.loc[index]['Close']
                    stock_amnt=update_stock_amnt(balance,curr_price)
                    trans_value=curr_price*stock_amnt
                    if run_type == 'ADJ' or 'REAL' :
                        balance=update_balance(balance,trans_value,action,intent)
                    update_pos(index,action,curr_price,stock_amnt,trans_value,intent,balance)    

        ########################################################################################################################
        #                                             Output positions to csv
        #                                             =======================
        ########################################################################################################################
        #write_csv(stock_to_trade,curr_date,positions)
        outname = "SMA-"+stock_to_trade+"-X-"+datetime.strftime(curr_date,"%Y-%m-%d")+".csv"
        outdir = '/output/'
        #outdir = 'C:\DEVOPS\python apps\spiderdoc\spiderdoc\outfile\positions\''
        fullname =  outdir + outname
        positions.to_csv(fullname)
    if (stock_not_avail):
        return
#var initialize

#run_type : FLT - no balance ,constatnt stock amount | ADJ - adjusts balance and stock amount each trade | REAL - Saves balance next day 

""" stock_to_trade = 'AAPL'
start_date_range = '2021-11-02'
end_date_range = '2021-11-22'
run_type = 'ADJ' """
file_path = '/input/'+symbols_file
Sym_file = open(file_path,"r")


if __name__ == '__main__':
    # start 4 worker processes
    with multiprocessing.Pool(processes=prallel_proc_amnt) as pool:
        pool.map_async(run_simulation,iterable=Sym_file).get()

