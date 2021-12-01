import os
import subprocess
from fsplit.filesplit import Filesplit
import multiprocessing.process
import shutil


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

def clear_dir(dirs):
    for dir in dirs:
        shutil.rmtree(dir,ignore_errors=True)
        os.mkdir(dir)
        subprocess.call(['chmod', '0666', dir])
    return    
                    
################################################################################################
#var inits
fs = Filesplit()
active_hosts=0
dirs_to_clear = ["/appcode/input/tmp/symbols","/appcode/spiderdoc/BT/input/"]
hostnames = ["BT-1","BT-2","BT-3","BT-4"]
active_hosts = []
Pros=[]

#clean up
clear_dir(dirs_to_clear)

#promts for run parms
start_date = input('enter start date in YYYY-mm-dd format : ')
end_date = input('enter end date in YYYY-mm-dd format : ')
print('FLT - no balance ,constatnt stock amount | ADJ - adjusts balance and stock amount each trade | REAL - Saves balance next day ')
run_type = input('enter run type(FLT|ADJ|REAL) : ')
containers_per_serv=input('how many containers on each server : ')
prallel_proc_amnt=input('how many parallel proces on each container : ')

#see how many servers are up
for host in hostnames:
    response = os.system("ping -c 1 " + host)
    if response == 0:
        active_hosts.append(host)
        print(host+' <===> is Online')
    else:
         pingstatus = "Network Error"
host_amnt=len(active_hosts)



#n servers are up . create from "Symbols" n files : Symbols_1,Symbols_2..Symbols_n
size_per_file = int((os.stat('Symbols').st_size) / host_amnt)+256
fs.split(file="/appcode/spiderdoc/BT/Symbols", split_size=size_per_file, output_dir="/appcode/input/tmp/symbols", newline=True)

#build containers on eatch server
for host in active_hosts:
    try:
        res= cmd_over_ssh(host,'docker build -t backtest:1.0.0 /appcode/spiderdoc/BT')
        print("Imaged Build Successfuly on Server : "+host)
    except:
        print("Build Failed On Server : "+host)
#start backtest.py on all active hosts at the same time with appropriate args
i=1
for host in active_hosts:
    p = multiprocessing.Process(target=cmd_over_ssh, args=(host,'python3 /appcode/spiderdoc/BT/backtest.py Symbols_'+str(i)+' '+start_date+' '+end_date+' '+run_type+' '+containers_per_serv+' '+prallel_proc_amnt))
    Pros.append(p)
    p.start()
    print("started backtest on :" + host)
    #used to specify to dest server which Symbols_n is his
    i += 1
 
 