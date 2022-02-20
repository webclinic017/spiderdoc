import alpaca_trade_api as tradeapi
import yfinance as yf
########## account info ############################
API_ID = 'PKSN7XLSQICEB8BLU4S9'
API_KEY = 'baOGnrJjAeBQfpe8Ql4NHfDwImo45RkkMUt2Vjat'
api_endpoint = 'https://paper-api.alpaca.markets'
####################################################
api = tradeapi.REST(key_id = API_ID,secret_key = API_KEY,base_url = api_endpoint)
list2 = []
list = api.list_assets()
file_p = '/home/ubuntu/spiderdoc/spiderdoc/Preprod/Trader/symbols.txt'
Sym_file = open(file_p,"w")
k = 0
for asset in list:
    if asset.tradable == True:
        list2.append(asset)

for asset in list2:
    try:
        df = yf.download(tickers=asset.symbol,period='60m',interval='1m')
        if len(df) > 1:
            Sym_file.write(asset.symbol+'\n')
            print(f"symbol {asset.symbol} Added - {k}/{i}")
            k += 1
    finally:
        i=+1