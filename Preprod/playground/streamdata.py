import datetime
import alpaca_trade_api as tradeapi
import pandas as pd
import websocket ,json
import talib
import config
import numpy as np
from itertools import compress


########## account info ############################
API_ID = 'PKAM4QPHOM4UPBGMF90C'
API_KEY = '9PdtZ8mifNBGKc8rnVfuZJRMVlFh7shCougkoMal'
api_endpoint = 'https://paper-api.alpaca.markets'
####################################################
def to_db(msg):
    global levels , in_position ,api
    df =pd.DataFrame()
    a_json = json.loads(msg)
    candle_open = a_json['o']
    candle_close = a_json['c']
    candle_high = a_json['h']
    candle_low = a_json['l']
    candle_ts = a_json['t']
                
    timestamps.append(candle_ts)
    opens.append(candle_open)
    closes.append(candle_close)
    highs.append(candle_high)
    lows.append(candle_low)
    
    df['Datetime'] = timestamps
    df['Open']  = opens
    df['High']  = highs
    df['Low']   = lows
    df['Close'] = closes
            
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





def on_open(ws):
    print("opened")
    global symbol
    auth_data ={"action": "auth", "key": "PKAM4QPHOM4UPBGMF90C", "secret": "9PdtZ8mifNBGKc8rnVfuZJRMVlFh7shCougkoMal"}
    

    ws.send(json.dumps(auth_data))
    listen_message = {"action":"subscribe","bars":[symbol]}

    ws.send(json.dumps(listen_message))
def on_message(ws, message):
    global api
    message = message[1:-1]
    print(message)
    to_db(message)
def on_close(ws,var1,var2):
    print("closed connection")

global opens,timestamps,closes,highs,lows,levels,symbol,api
opens = []
timestamps =[]
closes = []
highs = []
lows=[]
levels = []
symbol = input('enter sym name:')
api = tradeapi.REST(key_id = API_ID,secret_key = API_KEY,base_url = api_endpoint)


socket = "wss://stream.data.alpaca.markets/v2/iex"
ws = websocket.WebSocketApp(socket,on_open=on_open,on_message=on_message,on_close=on_close)
ws.run_forever()



# Get our account information.
account = api.get_account()
portfolio = api.list_positions()


print (str(len(api.list_positions())))
#api.submit_order(symbol='TSLA',qty=1,side='buy',type='market',time_in_force='gtc')
x = api.list_orders()

print(api.list_orders()[1].qty)

# Check if our account is restricted from trading.
if account.trading_blocked:
    print('Account is currently restricted from trading.')

# Check how much money we can use to open new positions.
print('${} is available as buying power.'.format(account.buying_power))


