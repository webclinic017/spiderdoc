import subprocess
import sys
import multiprocessing
from typing import Container
def start_container (line):
    global start_date_range
    global end_date_range
    global run_type
    subprocess.call(["docker", "run", "-v","/appcode/output/positions:/outfile/position", "backtest:1.0.0","--cpuset","1", line,start_date_range,end_date_range,run_type])

""" file = sys.argv[1]
start_date_range = sys.argv[2]
end_date_range = sys.argv[3]
run_type = sys.argv[4]   """

file = 'Symbols_1'
start_date_range = '2021-11-02'
end_date_range = '2021-11-20'
run_type = 'ADJ' 

file='/appcode/input/tmp/symbols/'+file
f = open(file, "r")
container_amnt = 4

pool = multiprocessing.Pool(processes=container_amnt)
while True:
    line=f.readline()
    pool.map_async(start_container,line)
