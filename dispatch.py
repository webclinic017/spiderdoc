import os
import paramiko
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
with open('Symbols') as infp:
    files = [open("Sym"+i+".txt" % i, 'w') for i in range(active_hosts)]
    for i, line in enumerate(infp):
        files[i % active_hosts].write(line)
    for f in files:
        f.close()
#get date range Arg / Prompt
start_date = '2021-11-02'
end_date = '2021-11-12'
#run computefor with args:start-date end-date Sym file suffix.

#use RSA private key to connect
k = paramiko.RSAKey.from_private_key_file("/home/ubuntu/.ssh/id_rsa")
ssh = paramiko.SSHClient()
i=1
for host in active_hosts:
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username='ubuntu', pkey=k)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('/appcode/spiderdoc/backtest '+'Sym'+i+".txt "+start_date+" "+end_date)
    i += 1