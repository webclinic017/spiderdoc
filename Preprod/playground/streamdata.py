import datetime
import alpaca_trade_api as tradeapi
import pandas as pd
import websocket ,json
import config
########## account info ############################
API_ID = 'PKNI20IYWW6VBFJ45L20'
API_KEY = 'KqgCbJH1KY3O8ydTXn60GUEZTOrOYnjLGmkIez0E'
api_endpoint = 'https://paper-api.alpaca.markets'
####################################################
def to_df(msg):
    global open
    df =pd.DataFrame()
    a_json = json.loads(msg)
    candle_open = a_json['o']
    candle_close = a_json['c']
    candle_high = a_json['h']
    candle_low = a_json['l']
    candle_ts = a_json['t']
    candle_exch = a_json['x']
    print(f"open : {candle_open} , close : {candle_close} , high : {candle_high} , low : {candle_low} AT EXCHANGE : {candle_exch}")
    if candle_exch == "FTX":
        
        
        timestamps.append(candle_ts)
        opens.append(candle_open)
        closes.append(candle_close)
        highs.append(candle_high)
        lows.append(candle_low)
        
        df['timestamp'] = timestamps
        df['Open']  = opens
        df['High']  = highs
        df['Low']   = lows
        df['Close'] = closes
        
        print(df)
    
    
   
    

def on_open(ws):
    print("opened")
    auth_data = {"action": "auth", "key": 'PKNI20IYWW6VBFJ45L20', "secret": 'KqgCbJH1KY3O8ydTXn60GUEZTOrOYnjLGmkIez0E'}
    

    ws.send(json.dumps(auth_data))

    listen_message = {"action":"subscribe","bars":["BTCUSD"]}

    ws.send(json.dumps(listen_message))
def on_message(ws, message):
    message = message[1:-1]
    to_df(message)

    

def on_close(ws,var1,var2):
    print("closed connection")

global opens,timestamps,closes,highs,lows
opens = []
timestamps =[]
closes = []
highs = []
lows=[]



socket = "wss://stream.data.alpaca.markets/v1beta1/crypto"

ws = websocket.WebSocketApp(socket,on_open=on_open,on_message=on_message,on_close=on_close)
ws.run_forever()


api = tradeapi.REST(key_id = API_ID,secret_key = API_KEY,base_url = api_endpoint)

# Get our account information.
account = api.get_account()

# Check if our account is restricted from trading.
if account.trading_blocked:
    print('Account is currently restricted from trading.')

# Check how much money we can use to open new positions.
print('${} is available as buying power.'.format(account.buying_power))


