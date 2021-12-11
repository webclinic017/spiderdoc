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
    global prallel_proc_amnt
    subprocess.call(["docker", "run", "-v","/containers/output:/output", "backtest:1.0.0", symbols_file,start_date_range,end_date_range,run_type,prallel_proc_amnt])
    

#args
file = sys.argv[1]
start_date_range = sys.argv[2]
end_date_range = sys.argv[3]
run_type = sys.argv[4]  
container_amnt = sys.argv[5]
prallel_proc_amnt = sys.argv[6]
#cast
container_amnt=int(container_amnt)

''' file = 'Symbols_1'
start_date_range = '2021-11-02'
end_date_range = '2021-11-20'
run_type = 'ADJ'
container_amnt = 4 '''


sym_list =[]
#used to specify for dest container which Symbols_n_m is his
for sufx in range(1,container_amnt+1):
    sym_list.append(file+'_'+str(sufx))   
containers_up=0
Pros=[]

#build new docker image
subprocess.call(["docker","build","-t", "backtest:1.0.0", "/appcode/spiderdoc/BT/containers/SMA/."])
subprocess.call(["docker","build","-t", "filebeat:17.6.0", "/appcode/spiderdoc/BT/containers/Filebeat/."])

#run filebeat image
subprocess.call(["docker", "run","-v","/containers/output:/var/log/trades/", "filebeat:17.6.0"])
#start containers serialy (to save RAM as CPU is at its maxUtil anyway)
pool = multiprocessing.Pool(1)
for sym in sym_list:
    pool.map(start_container,sym_list)
    
