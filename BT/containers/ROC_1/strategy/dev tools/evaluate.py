
from numpy import NaN, True_
import pandas as pd
import glob
from itertools import islice
from datetime import datetime,timedelta,time
import matplotlib.pyplot as plt
from pandas.core import indexing 

delta_positions=pd.DataFrame(columns=['Timestamp_start','Timestamp_end','Value','Intent'])
delta_long_position=pd.DataFrame(columns=['Timestamp_start','Timestamp_end','Value','Intent'])
delta_short_position=pd.DataFrame(columns=['Timestamp_start','Timestamp_end','Value','Intent'])
trades_won=pd.DataFrame(columns=['Timestamp_start','Timestamp_end','Value','Intent'])
trades_lost=pd.DataFrame(columns=['Timestamp_start','Timestamp_end','Value','Intent'])
def concat_positions():
    #get all data from csv into a single df - 0 rows deleted - open positions deleted
    path = "C:\\Users\\nolys\\Desktop\\results\\" # TODO:CHANGE PATH TO RELEVANT PATH FOR PROJECT
    all_files = glob.glob(path + "*.csv")
    li = []
    for filename in all_files:
        positions = pd.read_csv(filename)  #read single file
        positions = positions.drop('Timestamp', 1)
        positions = positions.iloc[1: , :]  #selects df from second row onward
        positions.rename(columns = {'Unnamed: 0':'Timestamp'}, inplace = True) 
        if(not positions.empty):
            if(positions.iloc[-1]['Intent'] == "SHORT" or positions.iloc[-1]['Intent'] == "LONG") :  #drop open positions at EOD
                positions.drop(index=positions.index[-1],axis=0, inplace=True) 
        li.append(positions)  #add file to concatination to list
    
        positions = pd.concat(li, axis=0)  #combine all files to single df
    positions= positions.reset_index(drop=True) #fix indexting issue
    return positions
def gen_delta_position():
    global positions
    global delta_positions
    delta_index= 0 
    for index, row in positions.iterrows():
        if positions.loc[index]["Intent"] == "CLOSE_LONG" :
            delta_positions.loc[delta_index,'Timestamp_start'] = positions.iloc[index-1]['Timestamp']
            delta_positions.loc[delta_index,'Timestamp_end'] = positions.iloc[index]['Timestamp']
            delta_positions.loc[delta_index,'Value'] = positions.iloc[index]['TValue'] - positions.iloc[index-1]['TValue']
            delta_positions.loc[delta_index,'Intent'] = 'LONG'
            delta_index += 1
        elif positions.iloc[index]["Intent"] == "CLOSE_SHORT" :
            delta_positions.loc[delta_index,'Timestamp_start'] = positions.iloc[index-1]['Timestamp']
            delta_positions.loc[delta_index,'Timestamp_end'] = positions.iloc[index]['Timestamp']
            delta_positions.loc[delta_index,'Value'] = positions.iloc[index-1]['TValue'] - positions.iloc[index]['TValue']
            delta_positions.loc[delta_index,'Intent'] = 'SHORT'
            delta_index += 1
        else:
            continue
    return delta_positions
def calc_gross_profit():
    global delta_positions
    gross_profit =0
    for index, row in islice(delta_positions.iterrows(), 0, None):
        if delta_positions.loc[index]["Value"] >= 0:
            gross_profit = gross_profit + delta_positions.loc[index]["Value"]
    return gross_profit
def gen_delta_positions_per_sym(sym):
    path = "C:\\Users\\nolys\\Desktop\\results\\" # TODO:CHANGE PATH TO RELEVANT PATH FOR PROJECT
    all_files = glob.glob(path +"*-"+sym+"-*.csv")
    li = []
    for filename in all_files:
        positions = pd.read_csv(filename)  #read single file
        positions.rename(columns = {'Unnamed: 0':'minute_in_day'}, inplace = True) 
        if(not positions.empty):
            if(positions.iloc[-1]['Intent'] == "SHORT" or positions.iloc[-1]['Intent'] == "LONG") :  #drop open positions at EOD
                positions.drop(index=positions.index[-1],axis=0, inplace=True) 
        li.append(positions)  #add file to concatination to list
    
        positions = pd.concat(li, axis=0)  #combine all files to single df
    positions= positions.reset_index(drop=True) #fix indexting issue
    return positions
    #my own attempt
def win_calc_streak():
    # save ram !
    global delta_positions 
    # final obj is df streak index_start index_end timestemp_s timestemp_e
    # create helper columns Results to set True\False if Winner (faster then putting it in for loop by a lot) 
    delta_positions["Result"] = delta_positions['Value'] > 0
    # instead of working on positions delta it self, we make a copy and work withit insted
    data = delta_positions
    # the helper row is used to find streaks by bools (comapres and checks if the next row does not have the same result)(winner and next is loser and vice versa is a streak reset )
    data['Start_of_streak'] = data['Result'].ne(data['Result'].shift())
    # helper row used in grouby later
    data['Streak_id'] = data.Start_of_streak.cumsum()
    
    data['Streak_counter'] = data.groupby('Streak_id').cumcount() + 1
    data['Cumm_val'] = data['Value'].cumsum()
    streaks = pd.concat([delta_positions,data['Result']], axis=1)
    streaks["Streak_start"] = data['Streak_counter'] == 1
    streaks["Streak_end"] = streaks["Streak_start"].shift(-1, fill_value=True)
    streaks.loc[streaks['Streak_start'], 'Start_time'] = streaks['Timestamp_start']
    streaks['Start_time']= streaks['Start_time'].fillna(method='ffill')
    streaks.loc[streaks['Streak_end'], 'End_time'] = streaks['Timestamp_start']
    streaks = streaks[streaks["Streak_end"] == True]
    save_first_cumm=streaks['Cumm_val'].iloc[0]
    streaks['Cumm_val'] = streaks['Cumm_val'] - streaks['Cumm_val'].shift() 
    streaks =streaks.fillna(save_first_cumm)
    streaks["Value"] =  streaks['Cumm_val']
    streaks=streaks[streaks["Streak_counter"] != 1]  
    streaks = streaks.drop(columns=["Timestamp_start","Timestamp_end","Result" ,"Streak_start", "Streak_end","Cumm_val","Start_of_streak"])    
    streaks = streaks.reset_index(drop = True)
    return streaks 



positions = concat_positions()
delta_positions = gen_delta_position()



delta_short_positions     = delta_positions[delta_positions['Intent'] == 'SHORT']
delta_long_positions      = delta_positions[delta_positions['Intent'] == 'LONG']
trades_won                = delta_positions[delta_positions["Value"] > 0]
trades_lost               = delta_positions[delta_positions["Value"] <= 0]
delta_long_positions_won  = delta_long_positions[delta_long_positions['Value'] > 0]
delta_short_positions_won = delta_short_positions[delta_short_positions['Value'] > 0]
## ================= MONEY =====================

gross_profit              = trades_won['Value'].sum()
gross_loss                = trades_lost['Value'].sum()
net_profit                = gross_profit + gross_loss
avg_profit                = trades_won['Value'].mean()
avg_loss                  = trades_lost['Value'].mean()
max_profit                = trades_won['Value'].max()
max_loss                  = trades_lost['Value'].max()
min_profit                = trades_won['Value'].min()
min_loss                  = trades_lost['Value'].min()
## ================= ACCURACY =====================
#delta_short_position = delta_short_position.reset_index(drop=True) - reindex from 0 to m | left with original index values from deleta_position for streak calculation.
#delta_long_position = delta_long_position.reset_index(drop=True)
delta_amount              = len(delta_positions.index)
short_amount              = len(delta_short_positions.index)
long_amount               = len(delta_long_positions.index)
trades_won_amnt           = len(trades_won.index)
trades_lost_amnt          = len(trades_lost.index)
longs_won                 = len(delta_long_positions_won.index)
shorts_won                = len(delta_short_positions_won.index)

percent_won               = (trades_won_amnt  / delta_amount ) * 100 
percent_loss              = (trades_lost_amnt / delta_amount ) * 100
try:
    percent_shrots_won        = (shorts_won / short_amount ) * 100
except :
    percent_shrots_won        = '-'
percent_longs_won         = (longs_won / long_amount ) * 100
# ================= STREAKS =========================
streaks = win_calc_streak()
win_streaks = streaks[streaks["Value"] > 0 ]
lose_streaks = streaks[streaks["Value"] <= 0 ]

win_streak_amount      = len(win_streaks.index)
lose_streak_amount     = len(lose_streaks.index)
#   PROFITS / LOSESS
avg_streak_profit      =   win_streaks['Value'].mean()
avg_streak_loss        =   lose_streaks['Value'].mean()
max_streak_profit      =   win_streaks['Value'].max()
max_streak_loss        =   lose_streaks['Value'].min()
min_streak_profit      =   win_streaks['Value'].min()
min_streak_loss        =   lose_streaks['Value'].max()
 #  TOTAL
avg_streak_length      = streaks['Streak_counter'].mean()
max_streak_length      = streaks['Streak_counter'].max()
min_streak_length      = streaks['Streak_counter'].min()
 #  WIN
avg_win_streak_length  = win_streaks['Streak_counter'].mean()
max_win_streak_length  = win_streaks['Streak_counter'].max()
min_win_streak_length  = win_streaks['Streak_counter'].min()
 #  LOSE :
avg_lose_streak_length = lose_streaks['Streak_counter'].mean()
max_lose_streak_length = lose_streaks['Streak_counter'].max()
min_lose_streak_length = lose_streaks['Streak_counter'].min()
#print(delta_positions)
#print(trades_won)
############################################## PRINTS ########################################
print('========= MONEY STATUS ============')
print("gross profits          : "+str(gross_profit))
print("gross losses           : "+str(gross_loss))
print("net profits            : "+str(net_profit))
print('=========== extra money info========')
print("avg_profit             : "+str(avg_profit))
print("avg_loss               : "+str(avg_loss))
print('========= ACCURACY ============')
print("Trades total           : "+str(len(delta_positions.index)))
print("Trades won             : " + str(len(trades_won.index))+"("+str(percent_won)+"%)")
print("Trades lost            : " + str(len(trades_lost.index))+"("+str(percent_loss)+"%)")
print("========= extra acuuracy info =======")
       
print("Shorts won             : "+str(shorts_won) +" ("+str(percent_shrots_won)+"%)")
print("Longs Won              : "+str(longs_won) +" ("+str(percent_longs_won)+"%)"  )



print(" ================STREA KS=================")
print("win_streak_amount      : "+     str(win_streak_amount) )
print("lose_streak_amount     : "+     str(lose_streak_amount))
 
print("avg_streak_profit      : "+   str(avg_streak_profit) )
print("avg_streak_loss        : "+   str(avg_streak_loss)   )
print("max_streak_profit      : "+   str(max_streak_profit) )
print("max_streak_loss        : "+   str(max_streak_loss)   )
print("min_streak_profit      : "+   str(min_streak_profit) )
print("min_streak_loss        : "+   str(min_streak_loss)   )
print(" ===========================================")
print("avg_streak_length      : "+   str(avg_streak_length) )
print("max_streak_length      : "+   str(max_streak_length) )
print("min_streak_length      : "+   str(min_streak_length) )
print("     ===========================================")
print("avg_win_streak_length  : "+    str(avg_win_streak_length))
print("max_win_streak_length  : "+    str(max_win_streak_length))
print("min_win_streak_length  : "+    str(min_win_streak_length))
print("    ============================================")
print("avg_lose_strak_length  : "+   str(avg_lose_streak_length))
print("min_lose_streak_length : "+     str(min_lose_streak_length))
print("max_lose_streak_length : "+     str(max_lose_streak_length))
print('#####################################################')
print('############# positions per symbols #################')
print('#####################################################')
file_path = 'C:\\Users\\nolys\\Desktop\\results\\symbols.txt'
Sym_file  = open(file_path,"r")
Daily_df = pd.DataFrame(columns=['Stock','Date','Daily_delta'])
Daily_df = Daily_df.loc[:,['Stock','Date','Daily_delta']]
k=0
for sym in Sym_file:
    sym=sym.strip('\n')
    positions_p_sym=gen_delta_positions_per_sym(sym)
    positions_p_sym = positions_p_sym.loc[:,['minute_in_day','Timestamp','Action','Amount','TValue','Intent',"Balance"]]
    df = positions_p_sym
   
    start_idx = 0
    do_calc   = False
    for i in range(1,df.shape[0]):
        pass
        minute = df['minute_in_day'][i]
        p_minute = df['minute_in_day'][i-1]

        if p_minute > minute:
            end_idx = i-1
            do_calc = True 
        if do_calc:
            EOD_balance_delta = df['Balance'][end_idx] - df['Balance'][start_idx]
            date = df['Timestamp'][i-1]
            date =datetime.strptime(date, '%Y-%m-%d %H:%M:%S%z').date()
            Daily_df.loc[k,'Stock']=sym
            Daily_df.loc[k,'Date']=date
            Daily_df.loc[k,'Daily_delta']=EOD_balance_delta
            
            k         +=1
            start_idx = i
            do_calc   = False
print(Daily_df)
        #set flag to true
        #when date changes set flag to flase
        #retrive previos pos from when the flag was set
    #avg day profit lose
    #max day profit loss
    #streak daily