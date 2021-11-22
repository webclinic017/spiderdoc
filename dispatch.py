import os
import paramiko
from fsplit.filesplit import Filesplit

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
k = paramiko.RSAKey.from_private_key_file("/home/ubuntu/.ssh/id_rsa")
ssh = paramiko.SSHClient()
i=1
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname=host, username='ubuntu', pkey=k)
for host in active_hosts:
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('docker build -t algo1d:1.0.0 /appcode/spiderdoc')
    print("GOT 1!")
for host in active_hosts:
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username='ubuntu', pkey=k)
    print("got here 2")
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('/appcode/spiderdoc/backtest /appcode/input/tmp/symbols/Symbols_'+str(i)+" "+start_date+" "+end_date)
    i += 1
