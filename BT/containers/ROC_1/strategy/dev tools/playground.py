from contextlib import nullcontext
from re import X
import yfinance as yf
import pandas as pd
import ta
import talib
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mpl_dates
from scipy.signal import argrelextrema
from sklearn.cluster import KMeans
from datetime import timedelta,time,datetime
import sys
import multiprocessing
from sklearn.metrics import silhouette_score

from itertools import compress
pd.options.mode.chained_assignment = None  # default='warn'

global candle_rankings

candle_rankings = {
        "CDL3LINESTRIKE_Bull": 1,
        "CDL3LINESTRIKE_Bear": 2,
        "CDL3BLACKCROWS_Bull": 3,
        "CDL3BLACKCROWS_Bear": 3,
        "CDLEVENINGSTAR_Bull": 4,
        "CDLEVENINGSTAR_Bear": 4,
        "CDLTASUKIGAP_Bull": 5,
        "CDLTASUKIGAP_Bear": 5,
        "CDLINVERTEDHAMMER_Bull": 6,
        "CDLINVERTEDHAMMER_Bear": 6,
        "CDLMATCHINGLOW_Bull": 7,
        "CDLMATCHINGLOW_Bear": 7,
        "CDLABANDONEDBABY_Bull": 8,
        "CDLABANDONEDBABY_Bear": 8,
        "CDLBREAKAWAY_Bull": 10,
        "CDLBREAKAWAY_Bear": 10,
        "CDLMORNINGSTAR_Bull": 12,
        "CDLMORNINGSTAR_Bear": 12,
        "CDLPIERCING_Bull": 13,
        "CDLPIERCING_Bear": 13,
        "CDLSTICKSANDWICH_Bull": 14,
        "CDLSTICKSANDWICH_Bear": 14,
        "CDLTHRUSTING_Bull": 15,
        "CDLTHRUSTING_Bear": 15,
        "CDLINNECK_Bull": 17,
        "CDLINNECK_Bear": 17,
        "CDL3INSIDE_Bull": 20,
        "CDL3INSIDE_Bear": 56,
        "CDLHOMINGPIGEON_Bull": 21,
        "CDLHOMINGPIGEON_Bear": 21,
        "CDLDARKCLOUDCOVER_Bull": 22,
        "CDLDARKCLOUDCOVER_Bear": 22,
        "CDLIDENTICAL3CROWS_Bull": 24,
        "CDLIDENTICAL3CROWS_Bear": 24,
        "CDLMORNINGDOJISTAR_Bull": 25,
        "CDLMORNINGDOJISTAR_Bear": 25,
        "CDLXSIDEGAP3METHODS_Bull": 27,
        "CDLXSIDEGAP3METHODS_Bear": 26,
        "CDLTRISTAR_Bull": 28,
        "CDLTRISTAR_Bear": 76,
        "CDLGAPSIDESIDEWHITE_Bull": 46,
        "CDLGAPSIDESIDEWHITE_Bear": 29,
        "CDLEVENINGDOJISTAR_Bull": 30,
        "CDLEVENINGDOJISTAR_Bear": 30,
        "CDL3WHITESOLDIERS_Bull": 32,
        "CDL3WHITESOLDIERS_Bear": 32,
        "CDLONNECK_Bull": 33,
        "CDLONNECK_Bear": 33,
        "CDL3OUTSIDE_Bull": 34,
        "CDL3OUTSIDE_Bear": 39,
        "CDLRICKSHAWMAN_Bull": 35,
        "CDLRICKSHAWMAN_Bear": 35,
        "CDLSEPARATINGLINES_Bull": 36,
        "CDLSEPARATINGLINES_Bear": 40,
        "CDLLONGLEGGEDDOJI_Bull": 37,
        "CDLLONGLEGGEDDOJI_Bear": 37,
        "CDLHARAMI_Bull": 38,
        "CDLHARAMI_Bear": 72,
        "CDLLADDERBOTTOM_Bull": 41,
        "CDLLADDERBOTTOM_Bear": 41,
        "CDLCLOSINGMARUBOZU_Bull": 70,
        "CDLCLOSINGMARUBOZU_Bear": 43,
        "CDLTAKURI_Bull": 47,
        "CDLTAKURI_Bear": 47,
        "CDLDOJISTAR_Bull": 49,
        "CDLDOJISTAR_Bear": 51,
        "CDLHARAMICROSS_Bull": 50,
        "CDLHARAMICROSS_Bear": 80,
        "CDLADVANCEBLOCK_Bull": 54,
        "CDLADVANCEBLOCK_Bear": 54,
        "CDLSHOOTINGSTAR_Bull": 55,
        "CDLSHOOTINGSTAR_Bear": 55,
        "CDLMARUBOZU_Bull": 71,
        "CDLMARUBOZU_Bear": 57,
        "CDLUNIQUE3RIVER_Bull": 60,
        "CDLUNIQUE3RIVER_Bear": 60,
        "CDL2CROWS_Bull": 61,
        "CDL2CROWS_Bear": 61,
        "CDLBELTHOLD_Bull": 62,
        "CDLBELTHOLD_Bear": 63,
        "CDLHAMMER_Bull": 65,
        "CDLHAMMER_Bear": 65,
        "CDLHIGHWAVE_Bull": 67,
        "CDLHIGHWAVE_Bear": 67,
        "CDLSPINNINGTOP_Bull": 69,
        "CDLSPINNINGTOP_Bear": 73,
        "CDLUPSIDEGAP2CROWS_Bull": 74,
        "CDLUPSIDEGAP2CROWS_Bear": 74,
        "CDLGRAVESTONEDOJI_Bull": 77,
        "CDLGRAVESTONEDOJI_Bear": 77,
        "CDLHIKKAKEMOD_Bull": 82,
        "CDLHIKKAKEMOD_Bear": 81,
        "CDLHIKKAKE_Bull": 85,
        "CDLHIKKAKE_Bear": 83,
        "CDLENGULFING_Bull": 84,
        "CDLENGULFING_Bear": 91,
        "CDLMATHOLD_Bull": 86,
        "CDLMATHOLD_Bear": 86,
        "CDLHANGINGMAN_Bull": 87,
        "CDLHANGINGMAN_Bear": 87,
        "CDLRISEFALL3METHODS_Bull": 94,
        "CDLRISEFALL3METHODS_Bear": 89,
        "CDLKICKING_Bull": 96,
        "CDLKICKING_Bear": 102,
        "CDLDRAGONFLYDOJI_Bull": 98,
        "CDLDRAGONFLYDOJI_Bear": 98,
        "CDLCONCEALBABYSWALL_Bull": 101,
        "CDLCONCEALBABYSWALL_Bear": 101,
        "CDL3STARSINSOUTH_Bull": 103,
        "CDL3STARSINSOUTH_Bear": 103,
        "CDLDOJI_Bull": 104,
        "CDLDOJI_Bear": 104 ,
        "CDLLONGLINE_Bull": 53,
        "CDLLONGLINE_Bear": 53,
        "CDLSHORTLINE_Bull": 85,
        "CDLSHORTLINE_Bear": 66,
        "CDLSTALLEDPATTERN_Bull": 93,
        "CDLSTALLEDPATTERN_Bear": 93,
        "CDLKICKINGBYLENGTH": 96,
        "CDLKICKINGBYLENGTH_Bear": 102
    }

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


def isSupport(df,i):
  support = df['Low'][i] < df['Low'][i-1]  and df['Low'][i] < df['Low'][i+1] and df['Low'][i+1] < df['Low'][i+2] and df['Low'][i-1] < df['Low'][i-2]
  return support

def isResistance(df,i):
  resistance = df['High'][i] > df['High'][i-1]  and df['High'][i] > df['High'][i+1] and df['High'][i+1] > df['High'][i+2] and df['High'][i-1] > df['High'][i-2]
  return resistance

def isFarFromLevel(l,levels,s):
   return np.sum([abs(l-x) < s  for x in levels]) == 0
#returns list of risk factor,if min / max  return null

def clean_levels(minute_ran):
    global levels
    global curr_stock_historical_bkp
    df =curr_stock_historical_bkp
    df['Datetime'] = pd.to_datetime(curr_stock_historical_bkp.index)
    df = curr_stock_historical_bkp.loc[:,['Datetime', 'Open', 'High', 'Low', 'Close','ema_thin','ema_med','ema_wide','trend']]
    df =curr_stock_historical_bkp.iloc[0:minute_ran,:]

    new_levels = []
    n=10
    range_arg_extrema_counts = 2
    curr_stock_historical_min = df.iloc[argrelextrema(df.Close.values, np.less_equal,
            order=n)[0]]['Low']
    curr_stock_historical_max = df.iloc[argrelextrema(df.Close.values, np.greater_equal,
            order=n)[0]]['High']
    curr_stock_historical_min['Datetime'] = pd.to_datetime(curr_stock_historical_min.index)
     
    curr_stock_historical_max['Datetime'] = pd.to_datetime(curr_stock_historical_max.index)

    for i in range(len(levels)):
        lvl_idx=levels[i][0]
        for k in range(len(curr_stock_historical_min.index)-1):
            s1 = str(curr_stock_historical_bkp['Datetime'][0])
            s2 = str(curr_stock_historical_min['Datetime'][k])

            format = '%Y-%m-%d %H:%M:%S%z'
            tdelta = datetime.strptime(s2, format) - datetime.strptime(s1, format)

            delta = tdelta.seconds / 60
            if lvl_idx in range(int(delta)-range_arg_extrema_counts,int(delta)+range_arg_extrema_counts):
                found_exrma_next_to_lvl =True
                new_levels.append((lvl_idx,levels[i][1]))
                
            """ if found_exrma_next_to_lvl==True:
            break  """         
        for k in range(len(curr_stock_historical_max.index)-1):
            s1 = str(curr_stock_historical_bkp['Datetime'][0])
            s2 = str(curr_stock_historical_max['Datetime'][k])

            format = '%Y-%m-%d %H:%M:%S%z'
            tdelta = datetime.strptime(s2, format) - datetime.strptime(s1, format)
            delta = tdelta.seconds / 60 
            
            if lvl_idx in range(int(delta)-range_arg_extrema_counts,int(delta)+range_arg_extrema_counts):
                new_levels.append((lvl_idx,levels[i][1]))
                found_exrma_next_to_lvl =True
                break
    return new_levels        
            
def show_plt(minute_ran):
    global curr_stock_historical_bkp
    global levels
    global positions
    curr_stock_historical_1 =curr_stock_historical_bkp.iloc[0:minute_ran,:]
    df = curr_stock_historical_bkp.iloc[:minute_ran+1,:]
    df['Datetime'] = pd.to_datetime(df.index)
    df = df.loc[:,['Datetime', 'Open', 'High', 'Low', 'Close']]
    
  
    n=7
    curr_stock_historical_min = curr_stock_historical_1.iloc[argrelextrema(curr_stock_historical_1.Close.values, np.less_equal,
            order=n)[0]]['Low']
    curr_stock_historical_max = curr_stock_historical_1.iloc[argrelextrema(curr_stock_historical_1.Close.values, np.greater_equal,
            order=n)[0]]['High']
    
    up = curr_stock_historical_bkp[curr_stock_historical_bkp.Close>=curr_stock_historical_bkp.Open]
    down = curr_stock_historical_bkp[curr_stock_historical_bkp.Close<curr_stock_historical_bkp.Open] 
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
    plt.subplots(2,1,sharex=True)

    plt.subplot(2,1,1)
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
    positions_long = positions[positions['Intent'] == "LONG"]
    positions_closed_longs = positions[positions['Intent'] == "CLOSE_LONG"]
    positions_short =  positions[positions['Intent'] == "SHORT"]
    positions_closed_short = positions[positions['Intent'] == "CLOSE_SHORT"]
    
    #draw s n r
    for level in levels:
        plt.hlines(level[1],xmin=df['Datetime'][level[0]],\
                xmax=max(df['Datetime']),colors='blue')    
    
    
    plt.scatter(positions_long.index,positions_long['Price'],marker='^',color="green")
    plt.scatter(positions_closed_longs.index,positions_closed_longs['Price'],marker='^',color="red")
    plt.scatter(positions_short.index,positions_short['Price'],marker='v',color="green")
    plt.scatter(positions_closed_short.index,positions_closed_short['Price'],marker='v',color="red")
    
    plt.scatter(curr_stock_historical_min.index, curr_stock_historical_min, c='r')
    plt.scatter(curr_stock_historical_max.index, curr_stock_historical_max, c='g')
    
    plt.subplot(2,1,2)
    plt.plot(curr_stock_historical.index,curr_stock_historical["roc_sma_15"],color='r')
    plt.axhline(y=0, color='b', linestyle='-')
    plt.plot(curr_stock_historical.index,curr_stock_historical["roc_sma_5"],color='g')

    #display candlestick chart ,EMA_[wide,med,thin] ,first n local min/max of 1st period of the day,
    plt.show()
   
def get_pattern_df(i):
    global curr_stock_historical
    global candle_rankings

    df = curr_stock_historical.iloc[:i,:]
    # extract OHLC 
    op = df['Open']
    hi = df['High']
    lo = df['Low']
    cl = df['Close']
    
    # create columns for each pattern
    for candle in candle_names:
        # below is same as;
        # df["CDL3LINESTRIKE"] = talib.CDL3LINESTRIKE(op, hi, lo, cl)
        df[candle] = getattr(talib, candle)(op, hi, lo, cl)
        
        #reduce helper cols in to one col
        
    df['candlestick_pattern'] = np.nan
    df['candlestick_match_count'] = np.nan
    for index, row in df.iterrows():

        # no pattern found
        if len(row[candle_names]) - sum(row[candle_names] == 0) == 0:
            df.loc[index,'candlestick_pattern'] = "NO_PATTERN"
            df.loc[index, 'candlestick_match_count'] = 0
        # single pattern found
        elif len(row[candle_names]) - sum(row[candle_names] == 0) == 1:
            # bull pattern 100 or 200
            if any(row[candle_names].values > 0):
                pattern = list(compress(row[candle_names].keys(), row[candle_names].values != 0))[0] + '_Bull'
                df.loc[index, 'candlestick_pattern'] = pattern
                df.loc[index, 'candlestick_match_count'] = 1
            # bear pattern -100 or -200
            else:
                pattern = list(compress(row[candle_names].keys(), row[candle_names].values != 0))[0] + '_Bear'
                df.loc[index, 'candlestick_pattern'] = pattern
                df.loc[index, 'candlestick_match_count'] = 1
        # multiple patterns matched -- select best performance
        else:
            # filter out pattern names from bool list of values
            patterns = list(compress(row[candle_names].keys(), row[candle_names].values != 0))
            container = []
            container_val = 0
            for pattern in patterns:
                if row[pattern] > 0:
                    container.append(pattern + '_Bull')
                    container_val += 1
                else:
                    container.append(pattern + '_Bear')
                    container_val -= 1
            rank_list = [candle_rankings[p] for p in container]
            if len(rank_list) == len(container):
                rank_index_best = rank_list.index(min(rank_list))
                df.loc[index, 'candlestick_pattern'] = container[rank_index_best]
                df.loc[index, 'pattern_val'] = container_val
                df.loc[index, 'candlestick_match_count'] = len(container)
    # clean up candle columns
    df['pattern_val']=df['pattern_val'].fillna(0)
    df.drop(candle_names, axis = 1, inplace = True)
    return df

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
    global candle_names
    global candle_rankings
    global positions
    global s
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
        exit_criteria_selecctor = 0
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

        #ema 60
        curr_stock_historical['ema_wide']= ta.trend.sma_indicator(curr_stock_historical['Close'],window=60,fillna=False)
        #ema 30
        curr_stock_historical['ema_med']= ta.trend.sma_indicator(curr_stock_historical['Close'],window=30,fillna=False)
        #ema 10
        curr_stock_historical['ema_thin']= ta.trend.sma_indicator(curr_stock_historical['Close'],window=10,fillna=False)
        
        #roc 
        curr_stock_historical["roc_thin"] = talib.ROC(curr_stock_historical['Close'], timeperiod = 5)
        #roc wide
        curr_stock_historical["roc_wide"] = talib.ROC(curr_stock_historical['Close'], timeperiod = 15)

        
        #roc sma        
        curr_stock_historical["roc_sma_15"] = talib.SMA(curr_stock_historical['roc_wide'], timeperiod = 5)

        #roc_roc_sma_30
        curr_stock_historical["roc_sma_5"] = talib.SMA(curr_stock_historical['roc_thin'], timeperiod = 5)
        
        
        #fill trend column
        conditions = [
            (curr_stock_historical['ema_wide'].lt(curr_stock_historical['ema_med'])) & (curr_stock_historical['ema_med'].lt(curr_stock_historical['ema_thin'])),
            (curr_stock_historical['ema_wide'].gt(curr_stock_historical['ema_med'])) & (curr_stock_historical['ema_med'].gt(curr_stock_historical['ema_thin'])),
            (curr_stock_historical['ema_wide'].gt(curr_stock_historical['ema_med'])) & (curr_stock_historical['ema_med'].lt(curr_stock_historical['ema_thin'])) & (curr_stock_historical['ema_wide'].lt(curr_stock_historical['ema_thin'])),
            (curr_stock_historical['ema_wide'].lt(curr_stock_historical['ema_med'])) & (curr_stock_historical['ema_med'].gt(curr_stock_historical['ema_thin'])) & (curr_stock_historical['ema_wide'].gt(curr_stock_historical['ema_thin'])),
            (curr_stock_historical['ema_med'].lt(curr_stock_historical['ema_thin'])) & (curr_stock_historical['ema_thin'].lt(curr_stock_historical['ema_wide'])) & (curr_stock_historical['ema_wide'].gt(curr_stock_historical['ema_med'])),
            (curr_stock_historical['ema_med'].gt(curr_stock_historical['ema_thin'])) & (curr_stock_historical['ema_thin'].gt(curr_stock_historical['ema_wide'])) & (curr_stock_historical['ema_wide'].lt(curr_stock_historical['ema_med']))
                    ]    
    
        choices = ['clear_up','clear_down',' up_shift_3',' down_shift_3','up_shift_2','down_shift_2']
        curr_stock_historical['trend'] = np.select(conditions, choices, default=0 )
        levels = []
        
        curr_stock_historical_bkp = curr_stock_historical
        
        s =  np.mean(curr_stock_historical['High'] - curr_stock_historical['Low'])    
        
        #for patter recognition (global to feach it ones only)    
        candle_names = talib.get_function_groups()['Pattern Recognition']
        
        pattern_df = pd.DataFrame(columns=["Datetime"])
        pattern_df =pattern_df.loc[:,['Datetime']]
        curr_stock_historical['Datetime'] = pd.to_datetime(curr_stock_historical.index)
        curr_stock_historical = curr_stock_historical.loc[:,['Datetime', 'Open', 'High', 'Low', 'Close','ema_thin','ema_med','ema_wide','trend','roc_sma_15','roc_sma_5']]
        ##########################################################################################################################
        #                                       RUN THROUGH DAY                                                                  #   
        ##########################################################################################################################
        for i in range(2,curr_stock_historical.shape[0]-2):
            #search for snr live
            if isSupport(curr_stock_historical,i):
                l = curr_stock_historical['Low'][i]
                if isFarFromLevel(l,levels,s):
                    levels.append((i,l))
                    levels = clean_levels(i)
            elif isResistance(curr_stock_historical,i):
                l = curr_stock_historical['High'][i]
                if isFarFromLevel(l,levels,s):
                    levels.append((i,l))
                    levels = clean_levels(i)
            
            #what was the intent of the previos trade in positions
            last_intent = positions.iloc[-1]['Intent']    
            #current close
            close=curr_stock_historical['Close'][i]                
            #show current state # TODO : remove            
            #if i % 30 == 0:
                #levels = clean_levels(i)
                #print(positions)  
        show_plt(i)

                
                    
                
                
            
stock_to_trade = 'AAPL'
start_date_range = '2021-12-22'
end_date_range = '2021-12-23'
run_type = 'ADJ'
run_simulation(stock_to_trade)
""" file_path = '/input/'+symbols_file
Sym_file = open(file_path,"r")


if __name__ == '__main__':
    # start n worker processes
    with multiprocessing.Pool(processes=prallel_proc_amnt) as pool:
        pool.map_async(run_simulation,iterable=Sym_file).get()   """