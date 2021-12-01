import subprocess
import sys
import os
import multiprocessing
from fsplit.filesplit import Filesplit

def start_container (symbols_file):
    global start_date_range
    global end_date_range
    global run_type
    global containers_up
    containers_up += 1
    subprocess.call(["docker", "run", "-v","/containers/output:/output", "backtest:1.0.0", symbols_file,start_date_range,end_date_range,run_type])

file = sys.argv[1]
start_date_range = sys.argv[2]
end_date_range = sys.argv[3]
run_type = sys.argv[4]  
container_amnt = sys.argv[5]
container_amnt=int(container_amnt) 

''' file = 'Symbols_1'
start_date_range = '2021-11-02'
end_date_range = '2021-11-20'
run_type = 'ADJ'
container_amnt = 4 '''

fs = Filesplit()

large_file_path='/appcode/input/tmp/symbols/'+file
size_per_file = int((os.stat(large_file_path).st_size) / container_amnt)+8
fs.split(file=large_file_path, split_size=size_per_file, output_dir="/appcode/spiderdoc/BT/input", newline=True)

sym_list =[]
for sufx in range(1,container_amnt+1):
    sym_list.append(file+'_'+str(sufx))
print(sym_list)    
containers_up=0
Pros=[]
#pool.map_async(start_container,sym_list) 
for sym in sym_list:
    start_container(sym_list)
    