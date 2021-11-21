from re import I
import alpaca_trade_api as tradeapi
import ta
import pandas as pd
import matplotlib.pyplot as plt 
import numpy as np 
import yfinance as yf
from datetime import datetime
from datetime import timedelta
from itertools import islice


#initialize
position_is_open=False
stock_to_trade = "AAPL"
positions = pd.DataFrame(columns=['Action','price','Amount','TValue'])


#api = tradeapi.REST('PK0GXVSBKQ0WO0B1CEUQ','CpcoieCzUchnKnRKWjjqLuVzGc5ECqrdvJGNnJrE','https://paper-api.alpaca.markets',)

# Get our account information.
#account = api.get_account()

# Check if our account is restricted from trading.
#if account.trading_blocked:
 #   print('Account is currently restricted from trading.')

# Check how much money we can use to open new positions.
#print('${} is available as buying power.'.format(account.buying_power))

#get historical data from yfinance
curr_stock_historical = yf.download(stock_to_trade,'2021-11-02','2021-11-03',interval='1m')
curr_stock_historical.head()

#calaculate SMA
curr_stock_historical['SMA']= ta.trend.sma_indicator(curr_stock_historical['Close'],window=10,fillna=True)
#current price - SMA 
close_relto_sma=curr_stock_historical['Close']-curr_stock_historical['SMA']

#cast into pandas df
close_relto_sma = pd.DataFrame(close_relto_sma)
curr_stock_historical_close=pd.DataFrame(curr_stock_historical['Close'])
curr_stock_historical_close.reindex()

stock_amnt=1000
for index, row in islice(close_relto_sma.iterrows(), 1, None):
    print(close_relto_sma.loc[index][0])
    prev_index = index - timedelta(minutes=1)
    closed_higher_then_prev =(curr_stock_historical_close.loc[index]>curr_stock_historical_close.loc[prev_index])
    above_sma =(close_relto_sma.loc[index]>0).all()
    print('above SMA:',above_sma,'| pos open?:',position_is_open)
    if ( (above_sma)& (position_is_open != True)):
            print('^^^BUY^^^')
    if ( above_sma & position_is_open==True) :
            print('^^^SELL^^^')
    #above SMA & Closed above prev LONG (Buy then Sell)
    if(position_is_open==False):
        if ( above_sma ) :
            position_is_open=True
            action='buy'
            trans_value=curr_stock_historical_close.loc[index]['Close']*stock_amnt
            positions.loc[index,'Action']=action
            positions.loc[index,'TValue']=trans_value
            positions.loc[index,'price']=curr_stock_historical_close.loc[index]['Close']
            positions.loc[index,'Amount']=stock_amnt
    if(position_is_open==True):
        if ( above_sma==False & position_is_open) :
            position_is_open=False
            action='sell'
            trans_value=curr_stock_historical_close.loc[index]['Close']*stock_amnt
            positions.loc[index,'Action']=action
            positions.loc[index,'Amount']=stock_amnt
            positions.loc[index,'price']=curr_stock_historical_close.loc[index]['Close']
            positions.loc[index,'TValue']=trans_value
print(positions)
total = 0
for index, row in islice(positions.iterrows(), 0, None):
    if positions.loc[index]["Action"] == "buy" :
        total = total - positions.loc[index]["TValue"]
    else:
        total = total + positions.loc[index]["TValue"]
print(total)
