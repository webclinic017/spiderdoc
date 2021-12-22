from contextlib import nullcontext
from re import X
from numpy.lib.function_base import append
import yfinance as yf
import pandas as pd
import ta
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mpl_dates
from scipy.signal import argrelextrema
from sklearn.cluster import KMeans
from datetime import timedelta,time,datetime
import sys
import multiprocessing
from sklearn.metrics import silhouette_score
from itertools import islice

get_rid_of_position = False
position_is_open=False
""" symbols_file = sys.argv[1]
start_date_range = sys.argv[2]
end_date_range = sys.argv[3]
run_type = sys.argv[4]
prallel_proc_amnt = sys.argv[5]
prallel_proc_amnt=int(prallel_proc_amnt) """

positions              = pd.DataFrame(columns=['Timestamp','Action','Amount','Price','TValue','Intent','Balance'])
#for eval 
positions_short        = pd.DataFrame(columns=['Action','Price','Amount','TValue','Intent'])
positions_closed_short = pd.DataFrame(columns=['Action','Price','Amount','TValue','Intent'])
positions_long         = pd.DataFrame(columns=['Action','Price','Amount','TValue','Intent'])
positions_closed_longs = pd.DataFrame(columns=['Action','Price','Amount','TValue','Intent'])
positions.set_index('Timestamp')
#assign before referance
########################################################################################################################
#                                           FUNCTIONS
########################################################################################################################

def update_pos(index,action,price,amount,tvalue,intent,balance) :
    global positions
    positions.loc[index,'Action']=action
    positions.loc[index,'Amount']=amount
    positions.loc[index,'Price']=price
    positions.loc[index,'TValue']=tvalue
    positions.loc[index,'Intent']=intent
    positions.loc[index,'Balance']=balance

def update_pos_long(index,action,amount,price,tvalue,intent) :
    positions_long .loc[index,'Action']=action
    positions_long.loc[index,'Amount']=amount
    positions_long.loc[index,'Price']=price
    positions_long.loc[index,'TValue']=tvalue
    positions_long.loc[index,'Intent']=intent
    
def update_pos_closed_long(index,action,amount,price,tvalue,intent) :
    positions_closed_longs.loc[index,'Action']=action
    positions_closed_longs.loc[index,'Amount']=amount
    positions_closed_longs.loc[index,'Price']=price
    positions_closed_longs.loc[index,'TValue']=tvalue
    positions_closed_longs.loc[index,'Intent']=intent
    
def update_pos_short(index,action,amount,price,tvalue,intent) :
    positions.loc[index,'Action']=action
    positions_short.loc[index,'Amount']=amount
    positions_short.loc[index,'Price']=price
    positions_short.loc[index,'TValue']=tvalue
    positions_short.loc[index,'Intent']=intent
    
def update_pos_closed_short(index,action,amount,price,tvalue,intent) :
    positions_closed_short.loc[index,'Action']=action
    positions_closed_short.loc[index,'Amount']=amount
    positions_closed_short.loc[index,'Price']=price
    positions_closed_short.loc[index,'TValue']=tvalue
    positions_closed_short.loc[index,'Intent']=intent

def update_balance (balance,trans_value,action,intent):  
    if (action == 'buy') :
        balance = balance - trans_value
    else:
        balance = balance + trans_value
    return balance
def update_stock_amnt (balance,stock_price,action):
    tmp_mod=balance % stock_price
    tmp_balace=balance-tmp_mod
    stock_amnt=tmp_balace / stock_price

    return stock_amnt

def k_clusters(kmax,x):
    sil = [None,None]
    kmax = 10

    # dissimilarity would not be defined for a single cluster, thus, minimum number of clusters should be 2
    for k in range(2, kmax+1):
        kmeans = KMeans(n_clusters = k)
        preds = kmeans.fit_predict(x.array.reshape(-1,1))
        
        centroids=kmeans.cluster_centers_
        sil.append(silhouette_score(x.array.reshape(-1,1), preds, metric = 'euclidean'))
    print("------------WSS_---------------------")
    print(sil)
    max_value = max(sil)
    max_index = sil.index(max_value) 
    return centroids[max_index]

def isSupport(df,i):
  support = df['Low'][i] < df['Low'][i-1]  and df['Low'][i] < df['Low'][i+1] and df['Low'][i+1] < df['Low'][i+2] and df['Low'][i-1] < df['Low'][i-2]
  return support

def isResistance(df,i):
  resistance = df['High'][i] > df['High'][i-1]  and df['High'][i] > df['High'][i+1] and df['High'][i+1] > df['High'][i+2] and df['High'][i-1] > df['High'][i-2]
  return resistance

def isFarFromLevel(l,levels,s):
   return np.sum([abs(l-x) < s  for x in levels]) == 0
#returns list of risk factor,if min / max  return null
def risk_fac(close,sr_pair):
    global curr_stock_historical
    print("srp -1----------------")
    print(str(sr_pair[-1]))
    print("====================")
    if str(sr_pair[-1]) == "max":
        return "max"
    elif str(sr_pair[-1]) == "min":
        return "min"
    elif sr_pair[-1] > close:
            print("res is : "+ str(sr_pair[-1]))
            print("sup is : "+str(sr_pair[0]))
            delta_res = abs(sr_pair[-1] - close)
            delta_sup = abs(close - sr_pair[0])
            sr_rate=delta_sup / delta_res
            return sr_rate
    elif sr_pair[-1] < close:
            print("res is : "+ str(sr_pair[0]))
            print("sup is : "+str(sr_pair[-1]))
            delta_res = abs(sr_pair[0] - close)
            delta_sup = abs(close - sr_pair[-1])
            sr_rate=delta_sup / delta_res
            return sr_rate        
               
def get_pair(close,snr):
    df = pd.DataFrame(columns=["level","delta"]) 
    i=0
    for level in snr:
        abs_delta=abs(close-level)
        df.loc[i,'level']=level
        df.loc[i,'delta']=abs_delta
        i += 1
    print(df)
    df.sort_values(by=['delta'],ascending=True)
    print(df)
    print(close)
    max=df["level"].max()
    min=df["level"].min()
    print("CLOSE : "+str(close))
    if(close > max ):
        return [max,"max"]
    elif (close < min) :
        return [min,"min"]
    else:
        return [df.iloc[-1]["level"],df.iloc[-2]["level"]]

def show_plt(minute_ran):
    global curr_stock_historical_bkp
    global levels
    curr_stock_historical_1 =curr_stock_historical_bkp.iloc[0:minute_ran,:]
    df = curr_stock_historical_bkp.iloc[:minute_ran+1,:]
    df['Datetime'] = pd.to_datetime(df.index)
    df = df.loc[:,['Datetime', 'Open', 'High', 'Low', 'Close']]
    print("==============LEVELS IN "+str(minute_ran)+" =====================")
    print(levels)
    for level in levels:
        plt.hlines(level[1],xmin=df['Datetime'][level[0]],\
                xmax=max(df['Datetime']),colors='blue')
    n=7
    curr_stock_historical_min = curr_stock_historical_1.iloc[argrelextrema(curr_stock_historical_1.Close.values, np.less_equal,
            order=n)[0]]['Low']
    curr_stock_historical_max = curr_stock_historical_1.iloc[argrelextrema(curr_stock_historical_1.Close.values, np.greater_equal,
            order=n)[0]]['High']
    
    up = curr_stock_historical_bkp[curr_stock_historical_bkp.Close>=curr_stock_historical_bkp.Open]
    down = curr_stock_historical_bkp[curr_stock_historical_bkp.Close<curr_stock_historical_bkp.Open] 
    plt.scatter(curr_stock_historical_min.index, curr_stock_historical_min, c='r')
    plt.scatter(curr_stock_historical_max.index, curr_stock_historical_max, c='g') 
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
    
    #create figure

    #define width of candlestick elements
    width = .0002
    width2 = .00002
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
    
def sell_short(i):
    global balance
    action='sell'
    intent = 'SHORT'
    curr_price =curr_stock_historical['Close'][i]
    stock_amnt=update_stock_amnt(balance,curr_price,action)
    trans_value=curr_price*stock_amnt
    if run_type == 'ADJ' or 'REAL' :
        balance=update_balance(balance,trans_value,action,intent)
    update_pos(curr_stock_historical['Datetime'][i],action,curr_price,stock_amnt,trans_value,intent,balance)

def close_short(i):
    global balance
    action='buy'
    intent = 'CLOSE_SHORT'
    curr_price =curr_stock_historical['Close'][i]
    stock_amnt =positions.iloc[-1]['Amount']
    trans_value=curr_price*stock_amnt
    if run_type == 'ADJ' or 'REAL' :
        balance=update_balance(balance,trans_value,action,intent)
    update_pos(curr_stock_historical['Datetime'][i],action,curr_price,stock_amnt,trans_value,intent,balance)  

def buy_long(i):
    global balance
    action='buy'
    intent = 'LONG'
    curr_price =curr_stock_historical['Close'][i]
    stock_amnt=update_stock_amnt(balance,curr_price,action)
    trans_value=curr_price*stock_amnt
    if run_type == 'ADJ' or 'REAL' :
        balance=update_balance(balance,trans_value,action,intent)
    update_pos(curr_stock_historical['Datetime'][i],action,curr_price,stock_amnt,trans_value,intent,balance)

def close_long(i):
    global balance
    action='sell'
    intent = 'CLOSE_LONG'
    curr_price =curr_stock_historical['SMA'][i]
    stock_amnt=positions.iloc[-1]['Amount']
    trans_value=curr_price*stock_amnt
    if run_type == 'ADJ' or 'REAL' :
        balance=update_balance(balance,trans_value,action,intent)
    update_pos(curr_stock_historical['Datetime'][i],action,curr_price,stock_amnt,trans_value,intent,balance)  

def get_support(i,close):
    global levels
    for level in reversed(levels):
       if level[1] <  close:
           return level[1]
    return 0 
def get_resistance(i,close):
    global levels
    for level in reversed(levels):
       if level[1] >  close:
           return level[1]
    return 0 

def set_stop_loss(i):
    global curr_stock_historical
    close = curr_stock_historical["Close"][i]
    trend = curr_stock_historical["trend"][i]
    sup = get_support(i,close)
    res= get_resistance(i,close)
    if trend == 'clear_up':
        print(str(((res-close)/close))+'/'+str(((res-close)/close)))
        rrr = ((res-close)/close) / ((close-sup)/sup)
    if trend == 'clear_down':
        print(str(((res-close)/close))+'/'+str(((res-close)/close)))
        rrr = ((close-sup)/sup) / ((res-close)/close)
    else:
        rrr = 0
    return rrr

def run_simulation(stock_to_trade):    
    get_rid_of_position = False
    position_is_open=False
    stock_not_avail = False
    global start_date_range 
    global end_date_range 
    global run_type 
    global snr
    global curr_stock_historical
    global curr_stock_historical_bkp
    global levels
    global balance
    stock_to_trade=stock_to_trade.strip('\n')
   
    a = datetime.strptime(start_date_range, "%Y-%m-%d")
    b = datetime.strptime(end_date_range, "%Y-%m-%d")
    delta_date = b - a
    #initialize position dataframe with null's ans 0's
    curr_date = start_date_range
    curr_date = datetime. strptime(curr_date, '%Y-%m-%d')
    curr_date=curr_date - timedelta(days=1) 
    balance = 10000

    for day in range(delta_date.days):
    #########################################################################################################################
    #                                           New Day initilazion
    #                                           ==================
    #########################################################################################################################                                            
        global positions
        positions              = pd.DataFrame(columns=['Timestamp','Action','Amount','Price','TValue','Intent'])
        #for eval 
        positions_short        = pd.DataFrame(columns=['Action','Price','Amount','TValue','Intent'])
        positions_closed_short = pd.DataFrame(columns=['Action','Price','Amount','TValue','Intent'])
        positions_long         = pd.DataFrame(columns=['Action','Price','Amount','TValue','Intent'])
        positions_closed_longs = pd.DataFrame(columns=['Action','Price','Amount','TValue','Intent'])
        curr_date=curr_date + timedelta(days=1) 
        update_pos('0000-00-00 00:00:00-00:00','NA',0,0,0,'NA',balance)
        if run_type != 'REAL' :
            balance=10000
        tommorow_date =curr_date + timedelta(days=1)
        get_rid_of_position = False 
        #skips loop run if staurday
        if curr_date.weekday() == 5 or curr_date.weekday() == 6 :
            continue
            #define up and down prices

        ########################################################################################################################
        #                                      Data and Metrics for this day are calculated Here
        #                                     ===================================================
        ########################################################################################################################
        #get historical data from yfinance for this day
        try:
            curr_stock_historical = yf.download(stock_to_trade,curr_date,tommorow_date,interval='1m')
            curr_stock_historical.head()
        except:
            stock_not_avail = True
            break
        up = curr_stock_historical[curr_stock_historical.Close>=curr_stock_historical.Open]
        down = curr_stock_historical[curr_stock_historical.Close<curr_stock_historical.Open] 

        curr_stock_historical_1 =curr_stock_historical.iloc[0:59,:]
        #ema 60
        curr_stock_historical['ema_wide']= ta.trend.sma_indicator(curr_stock_historical['Close'],window=60,fillna=False)
        #ema 30
        curr_stock_historical['ema_med']= ta.trend.sma_indicator(curr_stock_historical['Close'],window=30,fillna=False)
        #ema 10
        curr_stock_historical['ema_thin']= ta.trend.sma_indicator(curr_stock_historical['Close'],window=10,fillna=False)
        
        #fill trend column
        conditions = [
            (curr_stock_historical['ema_wide'].lt(curr_stock_historical['ema_med'])) & (curr_stock_historical['ema_med'].lt(curr_stock_historical['ema_thin'])) & (curr_stock_historical['ema_thin'].lt(curr_stock_historical['Close'])) ,
            (curr_stock_historical['ema_wide'].gt(curr_stock_historical['ema_med'])) & (curr_stock_historical['ema_med'].gt(curr_stock_historical['ema_thin'])) & (curr_stock_historical['ema_thin'].gt(curr_stock_historical['Close']))
                    ]    
    
        choices = ['clear_up','clear_down']
        curr_stock_historical['trend'] = np.select(conditions, choices, default=0 )
        levels = []
        curr_stock_historical_bkp = curr_stock_historical
        minute_ran=60
        from_time=0
        curr_stock_historical_prerun=curr_stock_historical.iloc[:minute_ran-1,:]
        curr_stock_historical_prerun['Datetime'] = pd.to_datetime(curr_stock_historical_prerun.index)
        curr_stock_historical_prerun = curr_stock_historical_prerun.loc[:,['Datetime', 'Open', 'High', 'Low', 'Close','ema_thin','ema_med','ema_wide','trend']]
        s =  np.mean(curr_stock_historical_prerun['High'] - curr_stock_historical_prerun['Low'])    
        for i in range(2,curr_stock_historical_prerun.shape[0]-2):
            if isSupport(curr_stock_historical_prerun,i):
                l = curr_stock_historical_prerun['Low'][i]
                if isFarFromLevel(l,levels,s):
                    levels.append((i,l))
            elif isResistance(curr_stock_historical_prerun,i):
                l = curr_stock_historical_prerun['High'][i]
                if isFarFromLevel(l,levels,s):
                    levels.append((i,l))
            print(str(i))
        show_plt(minute_ran)

        curr_stock_historical=curr_stock_historical_bkp.iloc[minute_ran:,:]
        curr_stock_historical['Datetime'] = pd.to_datetime(curr_stock_historical.index)
        curr_stock_historical = curr_stock_historical.loc[:,['Datetime', 'Open', 'High', 'Low', 'Close','ema_thin','ema_med','ema_wide','trend']]
        s =  np.mean(curr_stock_historical['High'] - curr_stock_historical['Low'])    
        print(curr_stock_historical)
        print(curr_stock_historical.shape[0])
        ##########################################################################################################################
        #                                       RUN THROUGH DAY                                                                  #   
        ##########################################################################################################################
        for i in range(2,curr_stock_historical.shape[0]-2):
            print(i)
            real_index = i + minute_ran 
            #set when to stop opening positions 
            close_time = 360
            print(curr_stock_historical['Datetime'][i])
            #checks if its closing time       
            if(close_time<i):
                get_rid_of_position = True
            #what was the intent of the previos trade in positions
            last_intent = positions.iloc[-1]['Intent']    
            #current close
            close=curr_stock_historical['Close'][i]
            #current identified trend
            trend = curr_stock_historical['trend'][i]

            #search for snr live
            print("REL :"+str(real_index))
            if isSupport(curr_stock_historical,i):
                l = curr_stock_historical['Low'][i]
                if isFarFromLevel(l,levels,s):
                    levels.append((real_index,l))
            elif isResistance(curr_stock_historical,i):
                l = curr_stock_historical['High'][i]
                if isFarFromLevel(l,levels,s):
                    levels.append((real_index,l))

            #show current state # TODO : remove            
            if i % 30 == 0:
                fig, ax = plt.subplots()
                show_plt(real_index)
            #############################################################
            #                     STRATEGY                              #
            #############################################################
            min_rrr = 1.2
            max_rrr = 2.5
            if (position_is_open==False ):
                if(trend=="clear_up"):
                    set_stop_loss=set_stop_loss(i)
                    print("risk reward ratio : "+str(rrr))
                    if rrr>min_rrr and rrr < max_rrr:
                        position_is_open=True
                        buy_long(i)
                        print("BL&")
                elif(trend=="clear_down"):
                    rrr=set_stop_loss(i)
                    print("risk reward ratio : "+str(rrr))
                    if (rrr>min_rrr) and (rrr < max_rrr):
                        position_is_open=True
                        sell_short(i)
                        print("SS&")
            #else:
                
            
stock_to_trade = 'AAPL'
start_date_range = '2021-12-13'
end_date_range = '2021-12-14'
run_type = 'ADJ'
run_simulation(stock_to_trade)
""" file_path = '/input/'+symbols_file
Sym_file = open(file_path,"r")


if __name__ == '__main__':
    # start n worker processes
    with multiprocessing.Pool(processes=prallel_proc_amnt) as pool:
        pool.map_async(run_simulation,iterable=Sym_file).get()   """