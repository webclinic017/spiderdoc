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
lines_per_file = num_lines = (int(sum(1 for line in open('Symbols'))) / i)+1
smallfile = None
filenum=1
with open('Symbols') as bigfile:
    for lineno, line in enumerate(bigfile):
        if lineno % lines_per_file == 0:
            if smallfile:
                smallfile.close()
            small_filename = '/appcode/input/tmp/symbols/sym'+str(filenum).format(lineno + lines_per_file)
            smallfile = open(small_filename, "w")
        smallfile.write(line)
    if smallfile:
        smallfile.close()
        filenum += 1
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
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('docker build -t SMA:1.0.0 /appcode/spiderdoc')
    print("GOT 1!")
for host in active_hosts:
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username='ubuntu', pkey=k)
    print("got here 2")
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('/appcode/spiderdoc/backtest /appcode/input/tmp/symbols/sym'+str(i)+" "+start_date+" "+end_date)
    i += 1
