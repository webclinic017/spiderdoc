import yfinance as yf
import pandas as pd
import matplotlib
import ta
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mpl_dates
from scipy.signal import argrelextrema
import random


def k_clusters(k,df):
    cluster_list = []
    passed = True
    print(df.values)
    index_length = len(df)
    #assign k random points
    for i in range(0,k):
        item_list=random.randint(0, index_length)
        for j in cluster_list:
            if j == item_list:  
                i -=1
                passed = False
                break
        if (passed ==True) :
            cluster_list.append(df.values[item_list])
    #calc diff from every number
    i = -1
    for max_p in df:
        for j in range(len(cluster_list)):
            delta_list=pd.DataFrame(columns=["cluster_num","delta"])
            print( str(max_p) +"----0---"+str(df.values[j]))
            i += 1
            cn=int(j) % (int(k))
            delta= max_p - df.values[j]
            delta_list.loc[i,'cluster_num']=cn
            delta_list.loc[i,'delta']=delta
        print('DDDDDDDDDDDDDDDDDDDDDD')
        print(delta_list)
    print("SSSSSSSSSSSSSSSSSSSSSSSS")
    print(delta_list)    
curr_stock_historical = yf.download("AAPL","2021-11-22","2021-11-23",interval='1m')

#create figure
plt.figure()

#define width of candlestick elements
width = .0002
width2 = .00002

#define up and down prices
up = curr_stock_historical[curr_stock_historical.Close>=curr_stock_historical.Open]
down = curr_stock_historical[curr_stock_historical.Close<curr_stock_historical.Open] 

n = 5  # number of points to be checked before and after

# Find local peaks

curr_stock_historical_min = curr_stock_historical.iloc[argrelextrema(curr_stock_historical.Close.values, np.less_equal,
                    order=n)[0]]['Close']
curr_stock_historical_max = curr_stock_historical.iloc[argrelextrema(curr_stock_historical.Close.values, np.greater_equal,
                    order=n)[0]]['Close']

# Plot results
max_resistance=k_clusters(3,curr_stock_historical_max)
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