from numpy.lib.function_base import append
import yfinance as yf
import pandas as pd
import matplotlib
import ta
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mpl_dates
from scipy.signal import argrelextrema
from sklearn.cluster import KMeans




def run_sim():
    curr_stock_historical = yf.download("TSLA","2021-11-22","2021-11-23",interval='1m')

    #create figure
    plt.figure()

    #define width of candlestick elements
    width = .0002
    width2 = .00002

    #define up and down prices
    up = curr_stock_historical[curr_stock_historical.Close>=curr_stock_historical.Open]
    down = curr_stock_historical[curr_stock_historical.Close<curr_stock_historical.Open] 

    curr_stock_historical_1 =curr_stock_historical.iloc[0:59,:]
    #ema 60
    curr_stock_historical['ema_wide']= ta.trend.sma_indicator(curr_stock_historical['Close'],window=60,fillna=False)
    #ema 30
    curr_stock_historical['ema_med']= ta.trend.sma_indicator(curr_stock_historical['Close'],window=30,fillna=False)
    #ema 10
    curr_stock_historical['ema_thin']= ta.trend.sma_indicator(curr_stock_historical['Close'],window=10,fillna=False)
    print("========================================================")
    print(curr_stock_historical)

    #define colors to use
    #bar and minmax colors

    col1 = 'green'
    col2 = 'red'
    #Ema
    #WIDE
    col3 = 'purple'
    #MED
    col4 = 'orange'
    #THIN
    col5 = 'cyan'
    #plot up prices
    plt.bar(up.index,up.Close-up.Open,width,bottom=up.Open,color=col1)
    plt.bar(up.index,up.High-up.Close,width2,bottom=up.Close,color=col1)
    plt.bar(up.index,up.Low-up.Open,width2,bottom=up.Open,color=col1)

    #plot down prices
    plt.bar(down.index,down.Close-down.Open,width,bottom=down.Open,color=col2)
    plt.bar(down.index,down.High-down.Open,width2,bottom=down.Open,color=col2)
    plt.bar(down.index,down.Low-down.Close,width2,bottom=down.Close,color=col2)
    plt.plot(curr_stock_historical.index,curr_stock_historical["ema_wide"],color=col3)
    plt.plot(curr_stock_historical.index,curr_stock_historical["ema_med"],color=col4)
    plt.plot(curr_stock_historical.index,curr_stock_historical["ema_thin"],color=col5)
    #rotate x-axis tick labels
    plt.xticks(rotation=45, ha='right')

    #display candlestick chart ,EMA_[wide,med,thin] ,first n local min/max of 1st period of the day,
    plt.show()
run_sim()