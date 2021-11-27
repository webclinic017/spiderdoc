import subprocess
import sys
import multiprocessing

file = sys.argv[1]
start_date_range = sys.argv[2]
end_date_range = sys.argv[3]
run_type = sys.argv[4]  

""" file = 'Symbols_1'
start_date_range = '2021-11-02'
end_date_range = '2021-11-03'
run_type = 'ADJ'  """
pros = []
file='/appcode/input/tmp/symbols/'+file
f = open(file, "r")
while True:
    line1 = f.readline()
    if not line1: break
    p = multiprocessing.Process(subprocess.call(["docker", "run", "-v","/appcode/output/positions:/outfile/position", "backtest:1.0.0", line1.rstrip('\n'),start_date_range,end_date_range,run_type]))
    pros.append(p)
    p.start()
    line2 = f.readline()
    if not line2: break
    p = multiprocessing.Process(subprocess.call(["docker", "run", "-v","/appcode/output/positions:/outfile/position", "backtest:1.0.0", line2.rstrip('\n'),start_date_range,end_date_range,run_type]))
    pros.append(p)
    p.start()
    line3 = f.readline()
    if not line3: break
    p = multiprocessing.Process(subprocess.call(["docker", "run", "-v","/appcode/output/positions:/outfile/position", "backtest:1.0.0", line3.rstrip('\n'),start_date_range,end_date_range,run_type]))
    pros.append(p)
    p.start()
    line4 = f.readline()
    if not line4: break
    p = multiprocessing.Process(subprocess.call(["docker", "run", "-v","/appcode/output/positions:/outfile/position", "backtest:1.0.0", line4.rstrip('\n'),start_date_range,end_date_range,run_type]))
    pros.append(p)
    p.start()
    