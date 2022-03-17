import os,subprocess,multiprocessing
import yfinance as yf
import alpaca_trade_api as tradeapi

def gen_sym_files():
    
    number_of_procs = 48
    sym_per_worker = 6917
    
    file_path = '/home/ubuntu/spiderdoc/Preprod/Trader/symbols.txt'
    #file_path = 'C:\DEVOPS\python apps\spiderdoc\spiderdoc\Preprod\symbols.txt'
    Sym_file = open(file_path,"r")
    x = len(Sym_file.readlines())
    Sym_file.close()

    Sym_file = open(file_path,"r")
    li= []
    for i in range(x):
        li.append(Sym_file.readline().strip('\n'))

    

    Sym_file.close()
    line = 0
    sym_count = int(x/sym_per_worker)
    for i in range(1,sym_count+1):
        file_path = 'C:\DEVOPS\python apps\spiderdoc\spiderdoc\Preprod\Trader\input\symbols_'+str(i)+'.txt'
        file_path = '/home/ubuntu/spiderdoc/Preprod/Trader/input/symbols_'+str(i)+'.txt'
        Sym_file = open(file_path,"a")
        for k in range(sym_per_worker):
            Sym_file.write(li[line]+'\n')
            line += 1
    print(str(sym_count))
    for i in range(1,sym_count+1):
        file_path = '/home/ubuntu/spiderdoc/Preprod/Trader/input/symbols_'+str(i)+'.txt'
        #file_path = 'C:\DEVOPS\python apps\spiderdoc\spiderdoc\Preprod\Trader\input\symbols_'+str(i)+'.txt'
        Sym_file = open(file_path,"r")
        x = len(Sym_file.readlines())
        Sym_file.close()
        li= []
        line=0
        
        Sym_file = open(file_path,"r")
        for m in range(x):
            li.append(Sym_file.readline().strip('\n'))
        
        for j in range (1,number_of_procs+1):   
            new_file_path = '/home/ubuntu/spiderdoc/Preprod/Trader/input/symbols_'+str(i)+"_"+str(j)+'.txt'
            final_Sym_file = open(new_file_path,"a")

            for k in range(int(x/number_of_procs)):
                final_Sym_file.write(li[line]+'\n')
                line += 1

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
""" active_hosts=0
Pros = []
hostnames = ["PP-1","PP-2","PP-3","PP-4"]

pool = multiprocessing.Pool(8)
active_hosts= pool.map_async(check_active_hosts,hostnames).get()
active_hosts = filter(None, active_hosts)
active_hosts=list(active_hosts)
print("actice host:" +str(len(active_hosts)))
print(active_hosts)
host_amnt = len(active_hosts)

i=1
paralle_amnt = 16
for host in active_hosts:
    p = multiprocessing.Process(target=cmd_over_ssh, args=(host,'python3 /appcode/spiderdoc/Preprod/lunchers/run_trader.py '+ str(i) +' '+paralle_amnt))
    Pros.append(p)
    p.start()
    print("started backtest on :" + host)
    #used to specify to dest server which Symbols_n is his
    i += 1 """

""" df = yf.download(tickers='AAPl',period='15m',interval='1m')
print(df) """
gen_sym_files()

""" ########## account info ############################
API_ID = 'PKFZO082H28QNDUQTHKK'
API_KEY = 'ZOFAh3LFePD13ZYUi19KMcQJHcyBDd5pMEIXJa4P'
api_endpoint = 'https://paper-api.alpaca.markets'
####################################################
api = tradeapi.REST(key_id = API_ID,secret_key = API_KEY,base_url = api_endpoint)
api.submit_order(symbol="IPGP",
    qty=1,side='sell',
    type='market',time_in_force='gtc',order_class='bracket',
    stop_loss={'stop_price': 110},
    take_profit={'limit_price': 108})
 """