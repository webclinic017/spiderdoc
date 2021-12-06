
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
    path = "C:\\DEVOPS\\python apps\\spiderdoc\\spiderdoc\BT\\container\\output\\" # TODO:CHANGE PATH TO RELEVANT PATH FOR PROJECT
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
#deprecated , somewhat inefficient ....
""" def calc_gross_loss():
    global delta_positions
    global positions_lost
    gross_loss =0    
    for index, row in islice(delta_positions.iterrows(), 0, None):
        if delta_positions.loc[index]["Value"] < 0:
            gross_loss = gross_loss + delta_positions.loc[index]["Value"]
    return gross_loss """
    #my own attempt
def win_calc_streak():
    #save ram
    global delta_positions 
    #final obj is df streak index_start index_end timestemp_s timestemp_e 
    delta_positions["Result"] = delta_positions['Value'] > 0
    data = delta_positions
    data['Start_of_streak'] = data['Result'].ne(data['Result'].shift())
    data['Streak_id'] = data.Start_of_streak.cumsum()
    data['Streak_counter'] = data.groupby('Streak_id').cumcount() + 1
    data['Cumm_val'] = data['Value'].cumsum()
    streaks = pd.concat([delta_positions, data['Streak_counter'],data['Result']], axis=1)
    print(streaks)
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
    streaks = streaks.drop(columns=["Timestamp_start","Timestamp_end","Result" ,"Streak_start", "Streak_end","Cumm_val"])
    print(streaks)
    return streaks 
def streak_summary():
    global win_streak
    
    return
    ## conditional for loop method (somewhat inefficient ...)
"""     for index,row in islice(delta_positions.iterrows(), 1, None):
        if delta_positions.loc[index]['Value'] > 0 :
            if delta_positions[index-1]['Value'] > 0:
                #raise win streak flag
                continue
            else :
                #lower win steak flag
                continue
        else :
            if delta_positions[index-1]['Value'] <= 0:
                #rais lose flag
                continue
            else:
                #lower streak flag
                continue """
                
#######end


positions = concat_positions()
delta_positions = gen_delta_position()
delta_amount    = len(delta_positions.index)

trades_won   = delta_positions[delta_positions["Value"] > 0]
trades_lost  = delta_positions[delta_positions["Value"] <= 0]

gross_profit = trades_won['Value'].sum()
gross_loss   = trades_lost['Value'].sum()
net_profit =   gross_profit + gross_loss
avg_profit =   trades_won['Value'].mean()
avg_loss   =   trades_lost['Value'].mean()
max_profit =   trades_won['Value'].max()
max_loss   =   trades_lost['Value'].max()
min_profit =   trades_won['Value'].min()
min_loss   =   trades_lost['Value'].min()
print(trades_won)
## ================= ACCURACY =====================
percent_won  = ( len(trades_won.index)  / delta_amount ) * 100 
percent_loss = ( len(trades_lost.index) / delta_amount ) * 100
delta_short_position = delta_positions[delta_positions['Intent'] == 'SHORT']
#delta_short_position = delta_short_position.reset_index(drop=True) - reindex from 0 to m | left with original index values from deleta_position for streak calculation.
delta_long_position = delta_positions[delta_positions['Intent'] == 'LONG']
#delta_long_position = delta_long_position.reset_index(drop=True)
# ================= STREAKS =========================
win_streak = win_calc_streak()
print(win_streak)
streak = streak_summary()
#print(delta_positions)
#print(trades_won)
print("==================WIM STREAK!================")
print(streak)
############################################## PRINTS ########################################
print('========= MONEY STATUS ============')
print("gross profits : "+str(gross_profit))
print("gross losses : "+str(gross_loss))
print("net profits : "+str(gross_loss))
print('=========== extra money info========')
print("avg_profit :"+str(avg_profit))
print("avg_loss : "+str(avg_loss))
print('========= ACCURACY ============')
print("Trades total :"+str(len(delta_positions.index)))
print("Trades won : " + str(len(trades_won.index))+"("+str(percent_won)+"%)")
print("Trades lost : " + str(len(trades_lost.index))+"("+str(percent_loss)+"%)")
print("========= extra acuuracy info =======")
print("")


"""
delta_positions.reset_index().plot.scatter(x = 'index', y = 'Value')
plt.grid(True)
plt.show()
print(delta_positions)         """
 