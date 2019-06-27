from protocol_const import *
import time, thread, json
import Requests as requests

MY_ID = 0
MY_TASKS = {}
FP = 0

def init(my_id):
    global MY_ID, FP
    MY_ID = my_id
    FP = open('Log/data_user.txt', 'a+', 0)

def init_task(router_id, timeout, datahash, code_bin):
    router_address = give_me_router_address(router_id)
    router_address += '/data_user/init_task/'
    router_address += str(MY_ID)

    print(router_address)

    ret = requests.post(router_address, data = {'timeout' : str(timeout), 'datahash' : datahash, 'code_bin' : code_bin}).text
    print(ret)
    return json.dumps(json.loads(ret))

def new_task(task_id, router_id):
    global MY_TASKS
    router_address = give_me_router_address(router_id)
    router_address += '/data_user/new_task/'
    router_address += str(MY_ID)
    computer_id = str(requests.post(router_address, data = {'task_id' : str(task_id)}).text)

    if(computer_id == 'None'):
        return 'None'

    print('Got Computer ' + str(computer_id))

    MY_TASKS[task_id] = {}
    MY_TASKS[task_id]['router_id'] = router_id

    FP.write(give_me_time() + 'DATA USER ' + str(MY_ID) + ' Assigning task id ' + str(task_id) + ' to computer id ' + str(computer_id) + '\n')

    return str(computer_id)

def start_task(code_bin, task_id, computer_id):

    print('In Data User Start Task')

    global MY_TASKS

    MY_TASKS[task_id]['code_bin'] = code_bin

    computer_address = give_me_computer_address(computer_id)
    computer_address += '/goto_work'

    requests.post(computer_address, data = {'code_bin' : str(code_bin), 'task_id' : task_id})

def print_output(task_id, return_value):
    fp = open('Test Files/task_id_' + str(task_id) + '.txt', 'w')
    fp.write(return_value)
    fp.close()

def end_task(task_id, return_value):
    global MY_TASKS
    MY_TASKS.pop(task_id)
    FP.write(give_me_time() + 'DATA USER ' + str(MY_ID) + ' Finished task id ' + str(task_id) + '\n')
    print_output(task_id, return_value)
    return return_value

def restart_task(task_id):

    FP.write(give_me_time() + 'DATA USER ' + str(MY_ID) + ' Restarting task id ' + str(task_id) + '\n')

    router_id = MY_TASKS[task_id]['router_id']
    code_bin = MY_TASKS[task_id]['code_bin']
    
    computer_id = str(new_task(task_id, router_id))
    start_task(code_bin, task_id, computer_id)

def print_all_task():
    global MY_TASKS
    ret = 'All tasks : <br/>'
    for task_id in MY_TASKS:
        ret += 'Task Number : %s working at Router Number : %d <br/>' % (task_id, MY_TASKS[task_id])
    
    return ret

def run(my_id):
    init(my_id)
    while True:
        time.sleep(1000)
