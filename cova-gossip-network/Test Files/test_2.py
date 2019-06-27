import requests, time, os, signal, json

def init_task(router_id, timeout, datahash, code_bin):
    address = 'http://localhost:' + str(router_id) + '/data_user/init_task/' + str(12000)
    print(address)
    return requests.post(address, data = {'timeout' : timeout, 'datahash' : datahash, 'code_bin' : code_bin}).text

def new_task(router_id, task_id):
    return str(requests.post('http://localhost:' + str(router_id) + '/data_user/new_task/' + str(12000), data = {'task_id' : task_id}).text)

def start_task(computer_id, task_id, code):
    requests.post('http://localhost:12000/start_task', data = {'computer_id' : str(computer_id), 'task_id' : str(task_id), 'code_bin' : str(code)})

def load_code(file_path):
    fp = open(file_path, 'r')
    return fp.read()

FP = open('../computer_logs.txt', 'r')

COMPUTER_ID = FP.read().split()
COMPUTER_ID = [int(i) for i in COMPUTER_ID]

def kill_computer(computer_id):
    os.kill(COMPUTER_ID[int(computer_id) - 11000 + 1], signal.SIGKILL)

datahash = 'nadimgukhay'
code_bin = load_code('data_user_code.py')

ret = json.loads(init_task(10000, 15, datahash, code_bin))

print(type(ret))
print(ret)

task_id = str(ret['task_id'])
cost = int(str(ret['cost']))

print(task_id, cost)

now_computer = new_task(10000, task_id)

print('Got Computer : ' + str(now_computer))

print(now_computer)

time.sleep(15)

kill_computer(now_computer)
