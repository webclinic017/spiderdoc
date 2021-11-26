#imports
from ntpath import join
import alpaca_trade_api as tradeapi
import ta
import pandas as pd
import matplotlib.pyplot as plt 
import numpy as np 
import yfinance as yf
from datetime import datetime,timedelta,time
from itertools import islice
import sys

#var initialize
get_rid_of_position = False
position_is_open=False

stock_to_trade = sys.argv[1]
start_date = sys.argv[2]
end_date = sys.argv[3]
# FLT - no balance ,constatnt stock amount | ADJ - adjusts balance and stock amount each trade | REAL - Saves balance next day 
run_type = sys.argv[4]
""" stock_to_trade = 'AAPL'
start_date = '2021-11-02'
end_date = '2021-11-03' """

positions              = pd.DataFrame(columns=['Action','Amount','Price','TValue','Intent'])
#for eval 
positions_short        = pd.DataFrame(columns=['Action','Price','Amount','TValue','Intent'])
positions_closed_short = pd.DataFrame(columns=['Action','Price','Amount','TValue','Intent'])
positions_long         = pd.DataFrame(columns=['Action','Price','Amount','TValue','Intent'])
positions_closed_longs = pd.DataFrame(columns=['Action','Price','Amount','TValue','Intent'])

####################################################################################################################################
def update_pos(index,action,price,amount,tvalue,intent) :
    positions.loc[index,'Action']=action
    positions.loc[index,'Amount']=amount
    positions.loc[index,'Price']=price
    positions.loc[index,'TValue']=tvalue
    positions.loc[index,'Intent']=intent
    
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

def update_balance (balance,trans_value,action):
    if action == "buy" :
        balance = balance - trans_value
    else:
        balance = balance + trans_value
    return balance

def update_stock_amnt (balance,stock_price):
    stock_amnt=balance / stock_price
    return stock_amnt
    
    
#####################################################################################################################################
#initialize position dataframe with null's ans 0's
update_pos('0000-00-00 00:00:00-00:00','NA',0,0,0,'NA')
balance=10000
stock_amnt=update_stock_amnt(balance)
#get historical data from yfinance
curr_stock_historical = yf.download(stock_to_trade,start_date,end_date,interval='1m')
curr_stock_historical.head()

#calaculate SMA of 15 minutes
curr_stock_historical['SMA']= ta.trend.sma_indicator(curr_stock_historical['Close'],window=15,fillna=True)
#current price reletive to SMA 
close_relto_sma=curr_stock_historical['Close']-curr_stock_historical['SMA']
#cast into pandas df
curr_stock_historical_close=pd.DataFrame(curr_stock_historical['Close'])
curr_stock_historical_close.reindex()

#5min rolling sum of Close to SMA
RS5m_close_relto_sma=pd.DataFrame(close_relto_sma,columns=['CRS'])
RS5m_close_relto_sma.rolling(5).sum()

#set stock amount to be traded
stock_amnt=1000
for index, row in curr_stock_historical['Close'].iteritems():
    prev_index = index - timedelta(minutes=1)
    current_time = time(index.hour, index.minute, index.second)
    
    #set when to stop opening positions 
    close_time = time(hour=15,minute=30,second=00)
    
    #what was the intent of the previos trade in positions
    last_intent = positions.iloc[-1]['Intent']
    
    #return int index instead of datetime
    index_int=(np.where(close_relto_sma.index==index)[0]).astype(int)

     #checks if its closing time       
    if(close_time<current_time):
        get_rid_of_position = True
    
    #if the difference between close and SMA is negetive its bellow SMA ,when higher then 0 its above
    above_sma =close_relto_sma.loc[index] > 0
    avg_above_sma =RS5m_close_relto_sma['CRS']> 0
    
    #true when stock price is above SMA
    if(above_sma):
        #no open positions and its not closing time - BUY LONG
        if(position_is_open == False and get_rid_of_position==False and avg_above_sma.loc[index]==True ):
            position_is_open=True
            action='buy'
            intent = 'LONG'
            curr_price =curr_stock_historical.loc[index]['Close']
            trans_value=curr_price*stock_amnt
            update_pos(index,action,curr_price,stock_amnt,trans_value,intent)
            if run_type == 'ADJ' or 'REAL' :
                balance=update_balance(balance,trans_value,action)
                stock_amnt=update_stock_amnt(balance)
                                
        #open position with a short intent = CLOSE SHORT
        elif(position_is_open == True and last_intent=="SHORT"):
            position_is_open=False
            action='buy'
            intent = 'CLOSE_SHORT'
            curr_price =curr_stock_historical.loc[index]['SMA']
            trans_value=curr_price*stock_amnt
            update_pos(index,action,curr_price,stock_amnt,trans_value,intent)
            if run_type == 'ADJ' or 'REAL' :
                balance=update_balance(balance,trans_value,action)
                stock_amnt=update_stock_amnt(balance)
    #
    elif( above_sma==False):
        if(position_is_open == True and last_intent=="LONG"):
            position_is_open=False
            action='sell'
            intent = 'CLOSE_LONG'
            curr_price =curr_stock_historical.loc[index]['SMA']
            trans_value=curr_price*stock_amnt
            update_pos(index,action,curr_price,stock_amnt,trans_value,intent)
            if run_type == 'ADJ' or 'REAL' :
                balance=update_balance(balance,trans_value,action)
                stock_amnt=update_stock_amnt(balance)
        elif(position_is_open == False and get_rid_of_position==False and avg_above_sma.loc[index] == False):
            position_is_open=True
            action='sell'
            intent = 'SHORT'
            curr_price =curr_stock_historical.loc[index]['Close']
            trans_value=curr_price*stock_amnt
            update_pos(index,action,curr_price,stock_amnt,trans_value,intent)
            if run_type == 'ADJ' or 'REAL' :
                balance=update_balance(balance,trans_value,action)
                stock_amnt=update_stock_amnt(balance)


outname = 'SMA-'+stock_to_trade+'-X-'+start_date+'.csv'
outdir = '/outfile/position/'
#outdir = 'C:\DEVOPS\python apps\spiderdoc\spiderdoc\outfile\positions\''
fullname =  outdir + outname
positions.to_csv(fullname)


