import psycopg2
import alpaca_trade_api as tradeapi
import websocket ,json
from datetime import datetime
########## account info ############################
API_ID = 'PKAM4QPHOM4UPBGMF90C'
API_KEY = '9PdtZ8mifNBGKc8rnVfuZJRMVlFh7shCougkoMal'
api_endpoint = 'https://paper-api.alpaca.markets'
####################################################
def to_db(msg):
    global in_position ,api,con,cur
    a_json = json.loads(msg)
    try:
        symbol       = a_json['sym']
        candle_open  = a_json['o']
        candle_close = a_json['c']
        candle_high  = a_json['h']
        candle_low   = a_json['l']        
        candle_ts    = a_json['s']
        candle_ts = datetime.fromtimestamp(candle_ts/1000).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return    
    
    cur.execute("insert into dbo.init_ohlc (symbol, timestamp, open, low, high, close) values (%s, %s, %s, %s, %s, %s)", 
                (symbol, candle_ts, candle_open,candle_low,candle_high, candle_close))
    con.commit()
    return
def on_open(ws):
    print("opened")
    global symbol
    auth_data ={"action": "auth", "params": "NYoCQ79AEJpaEDB4U4LwbZCN1RcZ7yIK"}
    ws.send(json.dumps(auth_data))
            
    listen_message = {"action":"subscribe", "params":"AM.*"}
    ws.send(json.dumps(listen_message))
    

def on_message(ws, message):
    global api
    #message = message[1:-1]
    message = message[1:-1]
    to_db(message)


def on_close(ws,var1,var2):
    print("closed connection")

global opens,timestamps,closes,highs,lows,api,con,cur
opens = []
timestamps =[]
closes = []
highs = []
lows=[]
api = tradeapi.REST(key_id = API_ID,secret_key = API_KEY,base_url = api_endpoint)

con = psycopg2.connect(host='10.1.0.4', database='postgres' ,user = 'postgres', password ='123123123')
cur = con.cursor()


socket = "wss://socket.polygon.io/stocks"
ws = websocket.WebSocketApp(socket,on_open=on_open,on_message=on_message,on_close=on_close)
ws.run_forever()




