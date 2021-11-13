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
buy_command_array = df = pd.DataFrame(columns=['Action'])

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
print(close_relto_sma)


for index, row in islice(close_relto_sma.iterrows(), 2, None):
    prev_index = index - timedelta(minutes=1)
     
    closed_higher_then_prev =(curr_stock_historical_close.loc[index]>curr_stock_historical_close.loc[prev_index]).any()
    above_sma =(row.values>0).any()
    print(above_sma)
    print(closed_higher_then_prev)
    #above SMA & Closed above prev LONG (Buy then Sell)
    if ( above_sma==True & (closed_higher_then_prev==True)) :
       buy_command_array.loc[index, 'Action'] = 'buy'
    #bellow SMA & Closed above prev SHORT (sell then buy)
    if (above_sma==True & (closed_higher_then_prev==True)) :
        buy_command_array.loc[index, 'Action'] = 'sell'
        #above SMA & Closed below prev CLOSE LONG (Buy then Sell)
    if (above_sma==False & (closed_higher_then_prev==False)) :
        buy_command_array.loc[index, 'Action'] = 'sell'
    #bellow SMA & Closed above prev CLOSE SHORT (sell then buy)
    if (above_sma==False & (closed_higher_then_prev==False)) :
        buy_command_array.loc[index, 'Action'] = 'buy' 
print(buy_command_array)
""" initial_datetime = datetime.strptime('2021-11-02 15:50:00-04:00', '%Y-%m-%d %H:%M:%S%z')
final_datetime = initial_datetime - timedelta(minutes=1)

print("currenr:",curr_stock_historical_close.loc[initial_datetime])
print("previos:",curr_stock_historical_close.loc[final_datetime]) """
plt.plot(curr_stock_historical['Close'])
plt.show()
