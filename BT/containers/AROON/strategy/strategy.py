import yfinance as yf
import pandas as pd
import talib
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta,time,datetime
from scipy.signal import argrelextrema
import sys
import multiprocessing
import time
pd.options.mode.chained_assignment = None  # default='warn'

get_rid_of_position = False
position_is_open=False
""" #symbols_file = sys.argv[1]
start_date_range = sys.argv[2]
end_date_range = sys.argv[3]
run_type = sys.argv[4]
prallel_proc_amnt = sys.argv[5] """

start_date_range = '2022-02-01'
end_date_range = '2022-02-23' 
run_type = 'REAL'
prallel_proc_amnt = 16

prallel_proc_amnt=int(prallel_proc_amnt) 

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

def update_pos(index,datetime,action,price,amount,tvalue,intent,balance) :
    global positions
    positions.loc[index,'Timestamp']=datetime
    positions.loc[index,'Action']=action
    positions.loc[index,'Amount']=amount
    positions.loc[index,'Price']=price
    positions.loc[index,'TValue']=tvalue
    positions.loc[index,'Intent']=intent
    positions.loc[index,'Balance']=balance

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

       
            
def show_plt(minute_ran,stock,start_date):
    global df
    global levels
    global positions
    #df = df.loc[:,['Datetime', 'Open', 'High', 'Low', 'Close']]
    

    n=7
    df_min = df.iloc[argrelextrema(df.Close.values, np.less_equal,
            order=n)[0]]['Low']
    df_max = df.iloc[argrelextrema(df.Close.values, np.greater_equal,
            order=n)[0]]['High']
    
    up = df_bkp[df_bkp.Close>=df_bkp.Open]
    down = df_bkp[df_bkp.Close<df_bkp.Open] 
    
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
    plt.subplots(3,1,sharex=True)
    plt.subplot(3,1,1)
    plt.title(stock+' '+start_date)
    #plot up prices
    plt.bar(up.index,up.Close-up.Open,width,bottom=up.Open,color=col1)
    plt.bar(up.index,up.High-up.Close,width2,bottom=up.Close,color=col1)
    plt.bar(up.index,up.Low-up.Open,width2,bottom=up.Open,color=col1)

    for level in levels:
        plt.hlines(level[1],xmin=df['Datetime'][level[0]],\
                xmax=max(df['Datetime']),colors='blue')
   
    plt.scatter(df_min.index, df_min, c='purple')
    plt.scatter(df_max.index, df_max, c='pink') 
    #plot down prices
    plt.bar(down.index,down.Close-down.Open,width,bottom=down.Open,color=col2)
    plt.bar(down.index,down.High-down.Open,width2,bottom=down.Open,color=col2)
    plt.bar(down.index,down.Low-down.Close,width2,bottom=down.Close,color=col2)
    
    #rotate x-axis tick labels
    plt.xticks(rotation=45, ha='right')
    positions_long = positions[positions['Intent'] == "LONG"]
    positions_closed_longs = positions[positions['Intent'] == "CLOSE_LONG"]
    positions_short =  positions[positions['Intent'] == "SHORT"]
    positions_closed_short = positions[positions['Intent'] == "CLOSE_SHORT"]
    
    plt.scatter(positions_long['Timestamp'],positions_long['Price'],marker='^',color="yellow")
    plt.scatter(positions_closed_longs['Timestamp'],positions_closed_longs['Price'],marker='^',color="orange")
    plt.scatter(positions_short['Timestamp'],positions_short['Price'],marker='v',color="yellow")
    plt.scatter(positions_closed_short['Timestamp'],positions_closed_short['Price'],marker='v',color="orange")
    
    plt.plot(df.index,df['ema60'],color='b')

    
    plt.subplot(3,1,2)
    plt.plot(df.index,df["aroonup"],color='b')
    plt.plot(df.index,df["aroondown"],color='orange')

    
    plt.subplot(3,1,3)
    
    
    
    
    #display candlestick chart ,EMA_[wide,med,thin] ,first n local min/max of 1st period of the day,
    plt.show()
    
def sell_short(i,stock_amnt_to_order):
    global balance
    global df

    action='sell'
    intent = 'SHORT'
    curr_price =df['Close'][i]
    stock_amnt=stock_amnt_to_order
    trans_value=curr_price*stock_amnt
    if run_type == 'ADJ' or 'REAL' :
        balance=update_balance(balance,trans_value,action,intent)
    update_pos(i,df['Datetime'][i],action,curr_price,stock_amnt,trans_value,intent,balance)

def close_short(i):
    global balance
    global df

    action='buy'
    intent = 'CLOSE_SHORT'
    curr_price =df['Close'][i]
    stock_amnt =positions.iloc[-1]['Amount']
    trans_value=curr_price*stock_amnt
    if run_type == 'ADJ' or 'REAL' :
        balance=update_balance(balance,trans_value,action,intent)
    update_pos(i,df['Datetime'][i],action,curr_price,stock_amnt,trans_value,intent,balance)  

def buy_long(i,stock_amnt_to_order):
    global balance
    global df
    action='buy'
    intent = 'LONG'
    curr_price =df['Close'][i]
    stock_amnt=stock_amnt_to_order
    trans_value=curr_price*stock_amnt
    if run_type == 'ADJ' or 'REAL' :
        balance=update_balance(balance,trans_value,action,intent)
    update_pos(i,df['Datetime'][i],action,curr_price,stock_amnt,trans_value,intent,balance)

def close_long(i):
    global balance
    global df

    action='sell'
    intent = 'CLOSE_LONG'
    curr_price =df['Close'][i]
    stock_amnt=positions.iloc[-1]['Amount']
    trans_value=curr_price*stock_amnt
    if run_type == 'ADJ' or 'REAL' :
        balance=update_balance(balance,trans_value,action,intent)
    update_pos(i,df['Datetime'][i],action,curr_price,stock_amnt,trans_value,intent,balance)     

def stock_amnt_order(close,level):
    global balance
    close_level_delta = abs(close-level)
    max_amnt=int(balance/close)
    max_tval=max_amnt * close
    starting_max_risk=close_level_delta*max_amnt
    desired_max_risk= balance * 0.02
    if starting_max_risk >= desired_max_risk:
        devide_coff=(starting_max_risk/desired_max_risk)
        stock_amnt_order = (max_amnt / devide_coff)
    else:
        stock_amnt_order=max_amnt
    return stock_amnt_order

def  get_pos_delta(close):
    global positions
    intent=positions.iloc[-1]['Intent']
    stock_amnt = positions.iloc[-1]['Amount']
    prev_price = positions.iloc[-1]['Price']
    if intent == "LONG":
        delta = (close - prev_price)* stock_amnt
    else:
        delta = (prev_price - close)* stock_amnt
    return delta
      

def enter_long(i):
    global df
    df=df
    close     = df['Close'][i]
    trend     = df['trend'][i]
    psar      = df['psar'][i]
    rsi       = df['rsi'][i]
    adx       = df['adx'][i] 
    pdi       = df['pdi'][i] 
    mdi       = df['mdi'][i] 
    
    au        = df['aroonup'][i]
    ad       = df['aroondown'][i]
      
    if trend == 'clear_up':
        if ad == 0 and au == 100:
            if psar < close:
                if rsi < 50:
                    if adx >= 25:
                        if pdi > mdi:
                            return True
    
        
    
    return False 
    
def exit_long(i,stop_loss,target_price):
    global df
    df=df
    
    close     = df['Close'][i]
    
    if close > target_price:
        print('TARGET REACHED')
        return True
    
    if close < stop_loss:
        print('STOP LOSS')
        return True
       
    return False

def enter_short(i):
    global df
    df=df
    close     = df['Close'][i]
    trend     = df['trend'][i]
    psar      = df['psar'][i]
    rsi       = df['rsi'][i]
    adx       = df['adx'][i] 
    pdi       = df['pdi'][i] 
    mdi       = df['mdi'][i] 
    
    au        = df['aroonup'][i]
    ad        = df['aroondown'][i]
      
    if trend == 'clear_down':   
        if au == 0 and ad == 100:
            if psar > close:
                if rsi > 30:
                    return True
       
        
    
    return False
    
    
def exit_short(i,stop_loss,target_price):
    global df
    df=df
    
    close     = df['Close'][i]
    
    if close < target_price:
        print('TARGET REACHED')
        return True
    
    if close > stop_loss:
        print('STOP LOSS')
        return True
       
    return False

    

def run_simulation(stock_to_trade):    
    get_rid_of_position = False
    position_is_open=False
    stock_not_avail = False
    global start_date_range 
    global end_date_range 
    global run_type 
    global snr
    global df
    global df_bkp
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
        positions              = pd.DataFrame(columns=['Timestamp','Action','Amount','Price','TValue','Intent','Balance'])
        #for eval 
        #positions['Timestamp'] = pd.to_datetime(positions.index)
        positions = positions.loc[:,['Timestamp','Action','Amount','Price','TValue','Intent',"Balance"]]

        curr_date=curr_date + timedelta(days=1) 
        if run_type != 'REAL' :
            balance=10000
        update_pos(0,'0000-00-00 00:00:00-00:00','NA',0,0,0,'NA',balance)

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
        #start_time = time.time()

        try:
            print(curr_date.strftime('%Y-%m-%d') + ' - ' + stock_to_trade)
            df = yf.download(stock_to_trade,curr_date,tommorow_date,interval='1m')
        except:
            stock_not_avail = True
            continue
        
        if df.isnull().values.any() or len(df) < 1:
            continue

        #ema 100
        
        
        df['ema60']= talib.SMA(df['Close'],timeperiod=60)
        
        df['psar'] = talib.SAR(df['High'], df['Low'], acceleration=0.02, maximum=0.2)
        
        df['rsi'] = talib.RSI(df['Close'], timeperiod=14)
        
        df['adx'] = talib.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)

        df['mdi'] = talib.MINUS_DI(df['High'],df['Low'], df['Close'], timeperiod=14)
        
        df['pdi'] = talib.PLUS_DI(df['High'],df['Low'], df['Close'], timeperiod=14)
        
        df['aroondown'], df['aroonup'] = talib.AROON(df['High'], df['Low'], timeperiod=14)
        #fill trend column
        conditions = [
            (df['ema60'].lt(df['Close'])),
            (df['ema60'].gt(df['Close']))
                    ]    
    
        choices = ['clear_up','clear_down']
        df['trend'] = np.select(conditions, choices, default=0 )
        levels = []
        
        df_bkp = df
                
        #for patter recognition (global to feach it ones only)    
        
        df['Datetime'] = pd.to_datetime(df.index)

        df = df.loc[:,['Datetime', 'Open', 'High', 'Low', 'Close','Volume','ema60','trend','psar','aroonup','aroondown','rsi','adx','pdi','mdi']]
        ##########################################################################################################################
        #                                       RUN THROUGH DAY                                                                  #   
        ##########################################################################################################################

        for i in range(df.shape[0]):
            #search for snr live
     
            #what was the intent of the previos trade in positions
            last_intent = positions.iloc[-1]['Intent']    
            #current close
            close=df['Close'][i]                
            #show current state # TODO : remove            
                
                #print(positions)  
            #############################################################
            #                     STRATEGY                              #
            #############################################################
            

            #possible to enter osotion only between 10:30 - 15:30 and when no positions are open
            if (position_is_open==False and i < 400 and i > 60):
                if(enter_long(i) == True):
                    position_is_open = True
                    stock_amnt_to_order = stock_amnt_order(close,df['psar'][i])
                    #PSAR is stop loss
                    target_price = close + (close- df['psar'][i])              
                    stop_loss = df['psar'][i]
                    buy_long(i,stock_amnt_to_order)
                    print( ' +++++++++++++++++++ ')
                    exit_select = 1
                elif(enter_short(i) == True):
                    position_is_open = True
                    stock_amnt_to_order = stock_amnt_order(close,df['psar'][i])
                    #PSAR is stop loss
                    target_price = close - (df['psar'][i] - close)             
                    stop_loss = df['psar'][i]
                    sell_short(i,stock_amnt_to_order)
                    print( ' +++++++++++++++++++ ')
                    exit_select = -1
                    
            elif ( position_is_open ==True):
                if exit_select == 1:
                    if (exit_long(i,stop_loss,target_price) == True):
                        position_is_open=False
                        close_long(i)
                        print( ' ============ ')
                        exit_select == 0
                        #DAY FINISHED COMPUTING
                elif  exit_select == -1:
                    if (exit_short(i,stop_loss,target_price) == True):
                        position_is_open=False
                        close_short(i)
                        print( ' ============ ')
                        exit_select == 0
                        #DAY FINISHED COMPUTING
                    

        last_intent = positions.iloc[-1]['Intent']    
        if last_intent == 'LONG':
            close_long(i)
            position_is_open = False
            
        if last_intent == 'SHORT':
            close_short(i)
            position_is_open = False
            
        outname = "ROC_1-"+stock_to_trade+"-X-"+datetime.strftime(curr_date,"%Y-%m-%d")+".csv"
        #outdir = '/output/'
        outdir = 'C:\\Users\\nolys\\Desktop\\results\\'
        fullname =  outdir + outname
        #print("--- %s seconds ---" % (time.time() - start_time))

        if len(positions) > 1:
            positions.to_csv(fullname)
            #show_plt(i,stock_to_trade,start_date_range)

        """ outname = "ROC_1-"+stock_to_trade+"-X-"+datetime.strftime(curr_date,"%Y-%m-%d")+"-STOCK.csv"
        #outdir = '/output/'
        outdir = 'C:\\Users\\nolys\\Desktop\\results\\'
        fullname =  outdir + outname
        df.to_csv(fullname)  """
        
            #pd.set_option('display.max_columns', None,'display.max_rows', None)
            #print(positions)               
                    
sim_scope = 0          
if sim_scope == 1:               
    stock_to_trade = 'AAPL'
    start_date_range = '2022-02-04'
    end_date_range = '2022-02-05'
    run_type = 'ADJ' 
    run_simulation(stock_to_trade)     
else :
    #file_path = '/input/Symbols'
    #file_path = '/home/ubuntu/spiderdoc/spiderdoc/BT/containers/ROC_1/input/Symbols'
    file_path = 'C:\\Users\\nolys\\Desktop\\results\\symbols.txt'
    Sym_file = open(file_path,"r")


    if __name__ == '__main__':
        # start n worker processes
        with multiprocessing.Pool(processes=prallel_proc_amnt) as pool:
            pool.map_async(run_simulation,iterable=Sym_file).get()  