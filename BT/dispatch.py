import os
import subprocess
from fsplit.filesplit import Filesplit
import multiprocessing
import shutil

active_hosts = []

################################################################################################
                            #functions
#this function starts a sub proc to run a cmd via ssh                           
def cmd_over_ssh (hosname,cmd):
    ssh = subprocess.Popen(["ssh", "%s" % hosname, cmd],
                       shell=False,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    result = ssh.stdout.readlines()
    if result == []:
        error = ssh.stderr.readlines()
    else:
        return result
def check_active_hosts(host):
    global active_hosts
    response = os.system("ping -c 1 " + host)
    if response == 0:
        print(host+' <===> is Online')
        return host
    else:
        pingstatus = "Network Error"
################################################################################################
#var inits
fs = Filesplit()
active_hosts=0
hostnames = ["BT-1","BT-2","BT-3","BT-4"]

Pros=[]



#promts for run parms
start_date = input('enter start date in YYYY-mm-dd format : ')
end_date = input('enter end date in YYYY-mm-dd format : ')
print('FLT - no balance ,constatnt stock amount | ADJ - adjusts balance and stock amount each trade | REAL - Saves balance next day ')
run_type = input('enter run type(FLT|ADJ|REAL) : ')
container_amnt=input('how many containers on each server : ')
prallel_proc_amnt=input('how many parallel proces on each container : ')

#see how many servers are up
pool = multiprocessing.Pool(8)
active_hosts= pool.map_async(check_active_hosts,hostnames).get()
active_hosts = filter(None, active_hosts)
active_hosts=list(active_hosts)
print("actice host:" +str(len(active_hosts)))
print(active_hosts)
host_amnt = len(active_hosts)
#clear the /containers/output dir on all servers with ansible
subprocess.call(["ansible-playbook","clear_last_run.yml"])

#clear ./input before spliting the master 'Symbols' file
shutil.rmtree('/appcode/spiderdoc/BT/input')
subprocess.call(["mkdir","./input/"])
#n servers are up . create from "Symbols" n files : Symbols_1,Symbols_2..Symbols_n | n-active_hosts
size_per_file = int((os.stat('Symbols').st_size) / host_amnt)+256
fs.split(file="/appcode/spiderdoc/BT/Symbols", split_size=size_per_file, output_dir="/appcode/spiderdoc/BT/input/", newline=True)

#m containers per server . create from "Symbols_n" m files : Symbols_n_1,Symbols_n_2..Symbols_n_m | n-active_hosts m-container amnt
for sym_suffix_host in range(1,len(active_hosts)+1):
    large_file_path='/appcode/spiderdoc/BT/input/Symbols_'+str(sym_suffix_host)
    size_per_file = int((os.stat(large_file_path).st_size) / int(container_amnt))+8
    fs.split(file=large_file_path, split_size=size_per_file, output_dir="/appcode/spiderdoc/BT/input/", newline=True)

#start backtest.py on all active hosts at the same time with appropriate args
i=1
for host in active_hosts:
    p = multiprocessing.Process(target=cmd_over_ssh, args=(host,'python3 /appcode/spiderdoc/BT/backtest.py Symbols_'+str(i)+' '+start_date+' '+end_date+' '+run_type+' '+container_amnt+' '+prallel_proc_amnt))
    Pros.append(p)
    p.start()
    print("started backtest on :" + host)
    #used to specify to dest server which Symbols_n is his
    i += 1
 
 