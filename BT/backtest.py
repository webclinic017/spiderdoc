import subprocess
import sys
import multiprocessing
from typing import Container
""" 
file = sys.argv[1]
start_date_range = sys.argv[2]
end_date_range = sys.argv[3]
run_type = sys.argv[4]       """

def run_command(line):
    global start_date_range
    global end_date_range
    global run_type 
    command = "docker run -v /appcode/output/positions:/outfile/position backtest:1.0.0 "+line+' '+start_date_range+' '+ end_date_range+' '+ run_type
    subprocess.Popen(command, shell=True) 

file = 'Symbols_1'
start_date_range = '2021-11-02'
end_date_range = '2021-11-03'
run_type = 'ADJ' 

pros = []
#file='/appcode/input/tmp/symbols/'+file
file='BT\Symbols'
container_amnt = 8
lines =[]
f = open(file, "r")
while True:
    for line_num in range(container_amnt) :
        line = f.readline()
        lines.append(line.rstrip('\n'))
    pool = multiprocessing.Pool(processes=container_amnt)
    pool.starmap(run_command,lines)