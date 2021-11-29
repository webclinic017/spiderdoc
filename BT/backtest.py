import subprocess
import sys
import os
import multiprocessing
from fsplit.filesplit import Filesplit
from typing import Container
def start_container (symbols_file):
    global start_date_range
    global end_date_range
    global run_type
    subprocess.call(["docker", "run", "-v","/containers:/outfile/position", "backtest:1.0.0", symbols_file,start_date_range,end_date_range,run_type])

""" file = sys.argv[1]
start_date_range = sys.argv[2]
end_date_range = sys.argv[3]
run_type = sys.argv[4]   """

file = 'Symbols_1'
start_date_range = '2021-11-02'
end_date_range = '2021-11-20'
run_type = 'ADJ'
container_amnt = 4
fs = Filesplit()

large_file_path='/appcode/input/tmp/symbols/'+file
size_per_file = int((os.stat(large_file_path).st_size) / container_amnt)+256
fs.split(file=large_file_path, split_size=size_per_file, output_dir="/containers/input", newline=True)


pool = multiprocessing.Pool(processes=container_amnt)
for i in container_amnt:
    container_input_file='/containers/input/'+file+'_'+i
    pool.map_async(start_container,(container_input_file))
