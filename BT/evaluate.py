
import pandas as pd
import glob
from itertools import islice
from datetime import datetime,timedelta,time
import matplotlib.pyplot as plt 

delta=pd.DataFrame(columns=['Value'])

#get all data from csv into a single df - 0 rows deleted - open positions deleted
path = 'C:\\Users\\Denis\\Desktop\\Project Money Printer\\money printer\\positions\\' # CHANGE PATH TO RELEVANT PATH FOR PROJECT
all_files = glob.glob(path + "*.csv")
print(all_files)
print(path)
li = []

for filename in all_files:
    positions = pd.read_csv(filename)  #read single file

    positions.drop(index=positions.index[0],axis=0, inplace=True)  #drop 0 rows

    if(not positions.empty):
        if(positions.iloc[-1]['Intent'] == "SHORT" or positions.iloc[-1]['Intent'] == "LONG") :  #drop open positions
           positions.drop(index=positions.index[-1],axis=0, inplace=True)

    li.append(positions)  #add file to list
   

positions = pd.concat(li, axis=0, ignore_index=True)  #combine all files to single df

#######end
    
#gross profit
total = 0
for index, row in islice(positions.iterrows(), 0, None):
    if positions.loc[index]["Action"] == "buy" :
        total = total - positions.loc[index]["TValue"]
    else:
        total = total + positions.loc[index]["TValue"]
print(total)
#end

#for eval
delta_index= 0 
for index, row in islice(positions.iterrows(), 0, None):
    if positions.loc[index]["Intent"] == "CLOSE_LONG" :
        delta.loc[delta_index] = positions.loc[index]['TValue'] - positions.loc[index-1]['TValue']
        delta_index += 1
    if positions.loc[index]["Intent"] == "CLOSE_SHORT" :
        delta.loc[delta_index] =positions.loc[index-1]['TValue'] - positions.loc[index]['TValue'] 
        delta_index += 1


delta.reset_index().plot.scatter(x = 'index', y = 'Value')
plt.grid(True)
plt.show()
print(delta)        
 