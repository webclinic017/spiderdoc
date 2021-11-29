import os
import sys
import subprocess
from fsplit.filesplit import Filesplit
import multiprocessing.process


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
                    
################################################################################################
#var definitions
fs = Filesplit()
active_hosts=0
hostnames = ["BT-1","BT-2","BT-3","BT-4"]
active_hosts = []
Pros=[]
start_date = input('enter start date in YYYY-mm-dd format : ')
end_date = input('enter end date in YYYY-mm-dd format : ')
print('FLT - no balance ,constatnt stock amount | ADJ - adjusts balance and stock amount each trade | REAL - Saves balance next day ')
run_type = input('enter run type(FLT|ADJ|REAL) : ')
containers_per_serv=2
#see how many servers are up
for host in hostnames:
    response = os.system("ping -c 1 " + host)
    if response == 0:
        active_hosts.append(host)
        print(host+' <===> is Online')
    else:
         pingstatus = "Network Error"

i=len(active_hosts)
#n servers are up . create from "Symbols" n files : Sym1,Sym2..Symn
size_per_file = int((os.stat('Symbols').st_size) / i)+256

fs.split(file="/appcode/spiderdoc/BT/Symbols", split_size=size_per_file, output_dir="/appcode/input/tmp/symbols", newline=True)
#get date range Arg / Prompt
i=1
for host in active_hosts:
    res= cmd_over_ssh(host,'docker build -t backtest:1.0.0 /appcode/spiderdoc/BT')

    print("GOT 1!")

for host in active_hosts:
    p = multiprocessing.Process(target=cmd_over_ssh, args=(host,'python3 /appcode/spiderdoc/BT/backtest.py Symbols_'+str(i)+' '+start_date+' '+end_date+' '+run_type+' '+containers_per_serv))
    Pros.append(p)
    p.start()
    print("started backtest on :" + host)
    i += 1
 
 