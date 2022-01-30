import subprocess,sys

def start_container (worker_num,proc_amnt):
    global start_date_range
    global end_date_range
    global run_type
    global containers_up
    global prallel_proc_amnt
    subprocess.call(["docker", "run", "-v","/containers/output:/output", "ROC_BT:1.0.0", worker_num,proc_amnt])
    

worker_num = sys.argv[1]
parllel_proc = sys.argv[2]

start_container(worker_num,parllel_proc)