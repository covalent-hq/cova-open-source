import requests, time, os, signal

def new_task(router_id, task_id):
    return int(str(requests.get('http://localhost:' + str(5200) + '/new_task/' + str(task_id) + '/' + str(router_id)).text))

FP = open('../computer_logs.txt', 'r')

COMPUTER_ID = FP.read().split()
COMPUTER_ID = [int(i) for i in COMPUTER_ID]

def kill_computer(computer_id):
    os.kill(COMPUTER_ID[computer_id + 1], signal.SIGKILL)

for i in range(6):
    new_task(0, i)