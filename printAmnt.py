import alpaca_trade_api as tradeapi

api = tradeapi.REST('PK0GXVSBKQ0WO0B1CEUQ','CpcoieCzUchnKnRKWjjqLuVzGc5ECqrdvJGNnJrE','https://paper-api.alpaca.markets',)

# Get our account information.
account = api.get_account()

# Check if our account is restricted from trading.
if account.trading_blocked:
    print('Account is currently restricted from trading.')

# Check how much money we can use to open new positions.
print('${} is available as buying power.'.format(account.buying_power))