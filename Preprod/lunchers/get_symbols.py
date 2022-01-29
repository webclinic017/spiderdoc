import alpaca_trade_api as tradeapi

########## account info ############################
API_ID = 'PKAM4QPHOM4UPBGMF90C'
API_KEY = '9PdtZ8mifNBGKc8rnVfuZJRMVlFh7shCougkoMal'
api_endpoint = 'https://paper-api.alpaca.markets'
####################################################
api = tradeapi.REST(key_id = API_ID,secret_key = API_KEY,base_url = api_endpoint)

list = api.list_assets()
file_p = 'C:\DEVOPS\python apps\spiderdoc\spiderdoc\Preprod\symbols.txt'
Sym_file = open(file_p,"w")
i = 0
for asset in list:
    Sym_file.write(asset.symbol+'\n')
    i += 1
    if i >= 2400:
        break