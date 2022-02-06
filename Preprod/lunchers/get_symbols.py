import alpaca_trade_api as tradeapi
import yfinance as yf
########## account info ############################
API_ID = 'PKLQW1C4WIB6XI2LOQ5W'
API_KEY = 'ohdklwFBMMMHbnpIjrUplgpYupnl7viaFofhbgyd'
api_endpoint = 'https://paper-api.alpaca.markets'
####################################################
api = tradeapi.REST(key_id = API_ID,secret_key = API_KEY,base_url = api_endpoint)
list2 = []
list = api.list_assets()
file_p = 'C:\DEVOPS\python apps\spiderdoc\spiderdoc\Preprod\symbols.txt'
Sym_file = open(file_p,"w")
i = 0
for asset in list:
    if asset.tradable == True:
        list2.append(asset)

for asset in list2:
    try:
        df = yf.download(tickers=asset.symbol,period='30m',interval='1m')
        if len(df) > 0:
            Sym_file.write(asset.symbol+'\n')
            print(f"symbol {asset.symbol} Added")
    finally:
        i += 1
        if i >= 8000:
            break  