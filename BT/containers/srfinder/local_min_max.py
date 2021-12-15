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



def k_clusters(k,df):
    cluster_list = []
    kmeans = KMeans(n_clusters=k).fit(df.array.reshape(-1,1))
    centroids = kmeans.cluster_centers_
    return centroids  
curr_stock_historical = yf.download("TSLA","2021-11-22","2021-11-23",interval='1m')

#create figure
plt.figure()

#define width of candlestick elements
width = .0002
width2 = .00002

#define up and down prices
up = curr_stock_historical[curr_stock_historical.Close>=curr_stock_historical.Open]
down = curr_stock_historical[curr_stock_historical.Close<curr_stock_historical.Open] 

n = 7  # number of points to be checked before and after (TODO: change n based on volitility)
x = np.array_split(curr_stock_historical,3)
for curr_stock_historical in x : 
    #set basic subset run parms
    max_resistance=[]
    min_support = []
    k=2
    n = 7  # number of points to be checked before and after (TODO: change n based on volitility)           
    curr_stock_historical_min = curr_stock_historical.iloc[argrelextrema(curr_stock_historical.Close.values, np.less_equal,
                    order=n)[0]]['Close']
    curr_stock_historical_max = curr_stock_historical.iloc[argrelextrema(curr_stock_historical.Close.values, np.greater_equal,
                    order=n)[0]]['Close']
    mxr=k_clusters(k,curr_stock_historical_max)
    mns=k_clusters(k,curr_stock_historical_min)
    max_resistance.append(mxr)
    min_support.append(mns)
    for y_val in max_resistance[-1]:
        plt.axhline(y = y_val, color ='r')
    for y_val in min_support[-1]:
        plt.axhline(y = y_val, color ='r')
    plt.scatter(curr_stock_historical_min.index, curr_stock_historical_min, c='r')
    plt.scatter(curr_stock_historical_max.index, curr_stock_historical_max, c='g')

    print("========================================================")
    print(curr_stock_historical)

    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")

    print(curr_stock_historical_max)
    print("VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV")
    print(curr_stock_historical_min)
    #define colors to use
    col1 = 'green'
    col2 = 'red'

    #plot up prices
    plt.bar(up.index,up.Close-up.Open,width,bottom=up.Open,color=col1)
    plt.bar(up.index,up.High-up.Close,width2,bottom=up.Close,color=col1)
    plt.bar(up.index,up.Low-up.Open,width2,bottom=up.Open,color=col1)

    #plot down prices
    plt.bar(down.index,down.Close-down.Open,width,bottom=down.Open,color=col2)
    plt.bar(down.index,down.High-down.Open,width2,bottom=down.Open,color=col2)
    plt.bar(down.index,down.Low-down.Close,width2,bottom=down.Close,color=col2)

    #rotate x-axis tick labels
    plt.xticks(rotation=45, ha='right')

    #display candlestick chart
    plt.show()