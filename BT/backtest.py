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
lines = []
file='/appcode/input/tmp/symbols/'+file
f = open(file, "r")
container_amnt=8
while True:
    for line_num in range(container_amnt):
        lines.append(f.readline())
        for line in lines:
            p = multiprocessing.Process(subprocess.call(["docker", "run", "-v","/appcode/output/positions:/outfile/position", "backtest:1.0.0", line.rstrip('\n'),start_date_range,end_date_range,run_type]))
            pros.append(p)
            p.start()
        if len(lines) < container_amnt:
            break
        lines=[]