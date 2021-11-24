import os
import paramiko
import sys
import subprocess
from fsplit.filesplit import Filesplit
################################################################################################
                            #functions
def cmd_over_ssh (hosname,cmd):
    ssh = subprocess.Popen(["ssh", "%s" % hosname, cmd],
                       shell=False,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    result = ssh.stdout.readlines()
    if result == []:
        error = ssh.stderr.readlines()
        print >>sys.stderr, "ERROR: %s" % error
    else:
        return result                         
################################################################################################
fs = Filesplit()
active_hosts=0
hostnames = ["BT-1","BT-2","BT-3","BT-4"]
active_hosts = []
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
size_per_file = int((os.stat('Symbols').st_size) / i)+1
smallfile = None
filenum=1
fs.split(file="/appcode/spiderdoc/Symbols", split_size=size_per_file, output_dir="/appcode/input/tmp/symbols", newline=True,)
#get date range Arg / Prompt
start_date = str('2021-11-02')
end_date = str('2021-11-12')
#run computefor with args:start-date end-date Sym file suffix.

#use RSA private key to connect
i=1
for host in active_hosts:
    res=cmd_over_ssh(host,'docker build -t backtest:1.0.0 /appcode/spiderdoc')
    print("GOT 1!")
for host in active_hosts:
    res=cmd_over_ssh(host,'/appcode/spiderdoc/backtest Symbols_'+str(i)+' '+start_date+' '+end_date)
    print("GOT 1!")
    i =+1
