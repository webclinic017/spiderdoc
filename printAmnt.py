import alpaca_trade_api as tradeapi
import ta
import pandas as pd
import matplotlib as plt
import yfinance as yf

api = tradeapi.REST('PK0GXVSBKQ0WO0B1CEUQ','CpcoieCzUchnKnRKWjjqLuVzGc5ECqrdvJGNnJrE','https://paper-api.alpaca.markets',)

# Get our account information.
account = api.get_account()

# Check if our account is restricted from trading.
if account.trading_blocked:
    print('Account is currently restricted from trading.')

# Check how much money we can use to open new positions.
print('${} is available as buying power.'.format(account.buying_power))
stock_to_trade = "AAPL"
curr_stock = yf.Ticker(stock_to_trade)
curr_stock_historical = curr_stock.history(start="2021-11-02", end="2021-11-03", interval="1m")
print(curr_stock_historical)