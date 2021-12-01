import subprocess
import sys
import os
import shutil
from fsplit.filesplit import Filesplit

def start_container (symbols_file):
    global start_date_range
    global end_date_range
    global run_type
    global containers_up
    global prallel_proc_amnt
    subprocess.call(["docker", "run", "-v","/containers/output:/output", "backtest:1.0.0", symbols_file,start_date_range,end_date_range,run_type,prallel_proc_amnt])
    return
def clear_dir(dirs):
    for dir in dirs:
        shutil.rmtree(dir,ignore_errors=True)
        os.mkdir(dir)
        subprocess.call(['chmod', '0666', dir])
    return
#args
file = sys.argv[1]
start_date_range = sys.argv[2]
end_date_range = sys.argv[3]
run_type = sys.argv[4]  
container_amnt = sys.argv[5]
prallel_proc_amnt = sys.argv[6]
#cast
container_amnt=int(container_amnt)
prallel_proc_amnt=int(prallel_proc_amnt)
''' file = 'Symbols_1'
start_date_range = '2021-11-02'
end_date_range = '2021-11-20'
run_type = 'ADJ'
container_amnt = 4 '''


#inits
fs = Filesplit()
dirs_to_clear = ['/containers/output']

#cleanup
clear_dir(dirs_to_clear)

#split Server-specific Symbol file into smaller packets for each container
large_file_path='/appcode/input/tmp/symbols/'+file
size_per_file = int((os.stat(large_file_path).st_size) / container_amnt)+8
fs.split(file=large_file_path, split_size=size_per_file, output_dir="/appcode/spiderdoc/BT/input", newline=True)

sym_list =[]
#used to specify for dest container which Symbols_n_m is his
for sufx in range(1,container_amnt+1):
    sym_list.append(file+'_'+str(sufx))   
containers_up=0
Pros=[]

#start containers serialy (to save RAM as CPU is at its maxUtil anyway)
for sym in sym_list:
    start_container(sym)
    