
import pandas as pd
import glob
from itertools import islice
from datetime import datetime,timedelta,time
import matplotlib.pyplot as plt 

delta_positions=pd.DataFrame(columns=['Timestamp_start','Timestamp_end','Value','Intent'])

def concat_positions():
    #get all data from csv into a single df - 0 rows deleted - open positions deleted
    path = "C:\\DEVOPS\\python apps\\spiderdoc\\spiderdoc\BT\\container\\output\\" # TODO:CHANGE PATH TO RELEVANT PATH FOR PROJECT
    all_files = glob.glob(path + "*.csv")
    li = []
    for filename in all_files:
        positions = pd.read_csv(filename)  #read single file
        positions = positions.drop('Timestamp', 1)
        positions = positions.iloc[1: , :]  #selects df from second row onward TODO: fix SMA.py so indexing is correct and is named "Timestamp"
        positions.rename(columns = {'Unnamed: 0':'Timestamp'}, inplace = True)
        if(not positions.empty):
            if(positions.iloc[-1]['Intent'] == "SHORT" or positions.iloc[-1]['Intent'] == "LONG") :  #drop open positions at EOD
                positions.drop(index=positions.index[-1],axis=0, inplace=True)
        li.append(positions)  #add file contance to list
    
    positions = pd.concat(li, axis=0)  #combine all files to single df
    positions= positions.reset_index(drop=True)
    return positions
def gen_delta_position():
    global positions
    global delta_positions
    delta_index= 0 
    for index, row in positions.iterrows():
        print("LOOK!!!!!!!!!!!!!!!!!")
        print('index :'+str(index)+' prev_index : '+str(index-1))
        if index > 1 :
            print(positions.loc[index-1]["TValue"])
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
    global positions_won
    gross_profit =0
    for index, row in islice(delta_positions.iterrows(), 0, None):
        if delta_positions.loc[index]["Value"] >= 0:
            gross_profit = gross_profit + delta_positions.loc[index]["Value"]
            positions_won +=1
    return gross_profit
def calc_gross_loss():
    global delta_positions
    global positions_lost
    gross_loss =0    
    for index, row in islice(delta_positions.iterrows(), 0, None):
        if delta_positions.loc[index]["Value"] < 0:
            gross_loss = gross_loss - delta_positions.loc[index]["Value"]
            positions_lost += 1
    return gross_loss

#######end

positions_won =0 #updates in calc_gross_profit
positions_lost =0 #updates in calc_gross_loss
positions = concat_positions()
print(positions)
delta_positions = gen_delta_position()
print(delta_positions)
"""delta_amount = len(delta_positions.index)
gross_profit = calc_gross_profit()
gross_loss = calc_gross_loss()
avg_profit = gross_profit / positions_won
avg_loss = gross_loss / positions_lost
percent_won = (delta_amount / positions_won) * 100 
percent_loss = (delta_amount / positions_lost) * 100



delta_positions.reset_index().plot.scatter(x = 'index', y = 'Value')
plt.grid(True)
plt.show()
print(delta_positions)         """
 