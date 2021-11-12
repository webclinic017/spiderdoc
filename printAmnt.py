import alpaca_trade_api as tradeapi

api = tradeapi.REST('PK0GXVSBKQ0WO0B1CEUQ','CpcoieCzUchnKnRKWjjqLuVzGc5ECqrdvJGNnJrE','https://paper-api.alpaca.markets',)

# Get our account information.
account = api.get_account()

# Check if our account is restricted from trading.
if account.trading_blocked:
    print('Account is currently restricted from trading.')

# Check how much money we can use to open new positions.
print('${} is available as buying power.'.format(account.buying_power))

# Get a list of all active assets.
print("active assets:")
active_assets = api.list_assets(status='active')

# Filter the assets down to just those on NASDAQ.
nasdaq_assets = [a for a in active_assets if a.exchange == 'NASDAQ']
print(nasdaq_assets)

# Check if AAPL is tradable on the Alpaca platform.
aapl_asset = api.get_asset('AAPL')
if aapl_asset.tradable:
    print('We can trade AAPL.')
