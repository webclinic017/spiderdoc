import psycopg2
import alpaca_trade_api as tradeapi
import websocket ,json

########## account info ############################
API_ID = 'PKAM4QPHOM4UPBGMF90C'
API_KEY = '9PdtZ8mifNBGKc8rnVfuZJRMVlFh7shCougkoMal'
api_endpoint = 'https://paper-api.alpaca.markets'
####################################################
def to_db(msg):
    global in_position ,api,con,cur
    a_json = json.loads(msg)
    symbol       = a_json['S']
    candle_open  = a_json['o']
    candle_close = a_json['c']
    candle_high  = a_json['h']
    candle_low   = a_json['l']
    candle_ts    = a_json['t']
    
    
    cur.execute("insert into dbo.init_ohlc (symbol, timestamp, open, low, high, close) values (%s, %s, %s, %s, %s, %s)", 
                (symbol, candle_ts, candle_open,candle_low,candle_high, candle_close))
    con.commit()

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

global opens,timestamps,closes,highs,lows,levels,symbol,api,con,cur
opens = []
timestamps =[]
closes = []
highs = []
lows=[]
levels = []
symbol = input('enter sym name:')
api = tradeapi.REST(key_id = API_ID,secret_key = API_KEY,base_url = api_endpoint)

con = psycopg2.connect(host='localhost', database='initial_ohlc_db' ,user = 'postgres', password ='Ariel2234')
cur = con.cursor()


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


