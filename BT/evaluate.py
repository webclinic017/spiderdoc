
import pandas as pd
import glob
from itertools import islice
from datetime import datetime,timedelta,time
import matplotlib.pyplot as plt 

delta=pd.DataFrame(columns=['Value'])
#get all data from csv into a single df
path = 'C:\\DEVOPS\\python apps\\spiderdoc\\spiderdoc\\automation\\outfile\\positions\\'
all_files = glob.glob(path + "*.csv")
print(all_files)
print(path)
li = []

for filename in all_files:
    positions = pd.read_csv(filename, index_col=[0])
    li.append(positions)

positions = pd.concat(li, axis=0, ignore_index=True)
print(positions)
total = 0
delta_index= 0 
for index, row in islice(positions.iterrows(), 0, None):
    if positions.loc[index]["Action"] == "buy" :
        total = total - positions.loc[index]["TValue"]
    else:
        total = total + positions.loc[index]["TValue"]
print(total)
#for eval
for index, row in islice(positions.iterrows(), 0, None):
    if positions.loc[index]["Intent"] == "CLOSE_LONG" :
        delta.loc[delta_index] = positions.loc[index]['TValue'] - positions.loc[index-1]['TValue']
        delta_index += 1
    if positions.loc[index]["Intent"] == "CLOSE_SHORT" :
        delta.loc[delta_index] =positions.loc[index-1]['TValue'] - positions.loc[index]['TValue'] 
        delta_index += 1

delta.plot.bar(y='Value', rot=0)
plt.show()
print(delta)        
