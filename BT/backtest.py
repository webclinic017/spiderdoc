import subprocess
import sys

file = sys.argv[1]
start_date_range = sys.argv[2]
end_date_range = sys.argv[3]
run_type = sys.argv[4]  

""" file = 'Symbols_1'
start_date_range = '2021-11-02'
end_date_range = '2021-11-03'
run_type = 'ADJ'  """

file='/appcode/input/tmp/symbols/'+file
f = open(file, "r")
while True:
    line1 = f.readline()
    if not line1: break
    subprocess.call(["docker", "run", "-v","/appcode/output/positions:/outfile/position", "backtest:1.0.0", line1,start_date_range,end_date_range,run_type])
    line2 = f.readline()
    if not line2: break
    subprocess.call(["docker", "run", "-v","/appcode/output/positions:/outfile/position", "backtest:1.0.0", line2,start_date_range,end_date_range,run_type])
    line3 = f.readline()
    if not line3: break
    subprocess.call(["docker", "run", "-v","/appcode/output/positions:/outfile/position", "backtest:1.0.0", line3,start_date_range,end_date_range,run_type])
    line4 = f.readline()
    if not line4: break
    subprocess.call(["docker", "run", "-v","/appcode/output/positions:/outfile/position", "backtest:1.0.0", line4,start_date_range,end_date_range,run_type])

    