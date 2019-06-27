from protocol_const import *
import time, thread, json, random, hashlib, string
from collections import deque
from datetime import datetime
from sets import Set
from pydblite.pydblite import Base
from database_helper import MemoryQueue, MemoryDict
import Requests as requests

MY_ID = 0
AVAILABILITY_LIST = {}
AVAILABLE_COMPUTERS_DEQUE = MemoryQueue('Available_Computer', ['computer_id', 'localtime'])
MY_TASK = MemoryDict('My_Task', 'task_id', ['data_user_id', 'computer_id', 'heartbeat', 'datahash', 'cost', 'timeout', 'code_bin'])
MY_SECRET = 0
FP = 0
PENDING_TASK = {}
CREDENTIALS = {}

UNDER_MY_WORKING = Set()

def join_req(computer_id):
    global AVAILABILITY_LIST
    AVAILABILITY_LIST[computer_id] = True

def set_secret(secret):
    global MY_SECRET
    MY_SECRET = str(secret)
    return 'Got Secret'

def init(my_id):
    global MY_ID, FP, CREDENTIALS
    MY_ID = my_id
    FP = open('Log/router.txt', 'a+', 0)

    if LOCAL:
        return

    address = 'http://localhost:5002/create_cred/d/' + str(MY_ID)

    CREDENTIALS = requests.get(address).text
    CREDENTIALS = json.loads(CREDENTIALS)

def make_computer_available(computer_id):
    global AVAIBILITY_LIST
    AVAILABILITY_LIST[computer_id] = True
    
def make_computer_unavailable(computer_id):
    global AVAIBILITY_LIST
    AVAILABILITY_LIST[computer_id] = False

def process_heartbeat(computer_id, localtime):
    global AVAILABLE_COMPUTERS_DEQUE
    AVAILABLE_COMPUTERS_DEQUE.push([computer_id, localtime])

def process_working_heartbeat(computer_id, localtime, task_id):
    global MY_TASK
    if(MY_TASK.len() > 0):
        print(computer_id, localtime, task_id)
    if MY_TASK.is_in(task_id):
        record = MY_TASK.give_me_elem(task_id)
        record[0]['heartbeat'] = localtime

def delete_expired_heartbeat():
    global AVAILABLE_COMPUTERS_DEQUE
    while True:
        if not AVAILABLE_COMPUTERS_DEQUE.is_empty():
            now_heartbeat = AVAILABLE_COMPUTERS_DEQUE.top()
            if int(time.mktime(datetime.now().timetuple())) - now_heartbeat['localtime'] > HEARTBEAT_CLEAR_TIME:
                AVAILABLE_COMPUTERS_DEQUE.pop()

        time.sleep(2)

def give_me_available_computer():
    global AVAILABLE_COMPUTERS_DEQUE

    while not AVAILABLE_COMPUTERS_DEQUE.is_empty():
        now_heartbeat = AVAILABLE_COMPUTERS_DEQUE.top()
        if AVAILABILITY_LIST[now_heartbeat['computer_id']]:
            return now_heartbeat['computer_id']
        AVAILABLE_COMPUTERS_DEQUE.pop()

    return None

def search_for_available_computer():

    computer_id = 'None'

    while True:
        random_router_id = random.randint(0, NUMBER_OF_ROUTERS - 1)
        random_router_id += 10000
        router_address = give_me_router_address(str(random_router_id))
        router_address += '/search_available'
        computer_id = str(requests.post(router_address).text)
        if computer_id == 'None':
            continue
        return str(computer_id)

def task_id_generator():
    letters = string.ascii_lowercase
    random_string = str(int(time.time()))
    random_string += ''.join(random.choice(letters) for i in range(3))
    return random_string

def cost_function(timeout):
    return 100

def init_task(data_user_id, timeout, datahash, code_bin):

    global PENDING_TASK
    task_id = task_id_generator()

    cost = cost_function(timeout)

    PENDING_TASK[task_id] = {'data_user_id' : data_user_id, 'cost' : cost, 'timeout' : timeout, 'datahash' : datahash, 'code_bin' : code_bin}

    print(PENDING_TASK)

    return json.dumps({'task_id' : task_id, 'cost' : cost})

def check_for_agreement(data_user_id, task_id):

    global PENDING_TASK

    if MY_TASK.is_in(task_id):
        return True

    if task_id not in PENDING_TASK:
        print('Task Id Is not in Pending Task')
        return False

    if LOCAL:
        return True

    address = 'http://localhost:5000/payment/seeAgreement/' + task_id

    print(address)

    try:
        ret = requests.get(address).text
    except:
        print('Could not connect to agreement')
        return False

    print(ret)

    try:
        ret = json.loads(ret)
    except:
        print('Could not convert')
        return False

    print(ret)

    if(int(str(ret['2']))<PENDING_TASK[task_id]['cost']):
        print('Agreement is not created')
        return False

    datahash = PENDING_TASK[task_id]['datahash']

    if(str(ret['1']) != datahash):
        print('Datahash is not same')
        return False

    return True

def get_data_link(datahash):
    global MY_ID

    if LOCAL:
        return 'cova.com'

    address = 'http://localhost:5001/get_keyfrag/' + str(datahash) + '/' + str(MY_ID)

    try:
        ret = requests.get(address).text
    except:
        print('Cannot Get Datahash in get_data_link')
        return 'sad.com'

    ret = json.loads(ret)

    try:
        ret = ret['metadata']['metadata']['data_link']
    except:
        print('Cannot retrieve in get_data_link')
        return 'sad.com'

    return str(ret)

def dec_key_fragment(datahash):

    global MY_ID

    if LOCAL:
        return 'my_key' + str(MY_ID)

    address = 'http://localhost:5001/get_keyfrag/' + str(datahash) + '/' + str(MY_ID)

    try:
        ret = requests.get(address).text
    except:
        print('Key Fragment Getting Error')
        return datahash + str(MY_ID)

    ret = json.loads(ret)

    if not ret['success']:
        print('Key Fragment Not Present')
        return datahash + str(MY_ID)

    ret = str(ret['keyfrag'])

    address = 'http://localhost:5002/decrypt'

    try:
        private_key = str(CREDENTIALS['rsa_cred']['privateKey'])
    except:
        print('Private Key Parsing Error')
        return datahash + str(MY_ID)

    try:
        ret = str(requests.post(address, data = {'enc_data' : ret, 'private_key' : private_key}).text)
    except:
        print('Decryption Error')
        return datahash + str(MY_ID)

    return ret

def new_task(data_user_id, task_id):

    if not check_for_agreement(data_user_id, task_id):
        return 'None'

    global UNDER_MY_WORKING, MY_TASK, PENDING_TASK

    if MY_TASK.is_in(task_id):
        record = MY_TASK.give_me_elem(task_id)
        cost = record[0]['cost']
        timeout = record[0]['timeout']
        datahash = record[0]['datahash']
        code_bin = record[0]['code_bin']
    elif task_id in PENDING_TASK:
        cost = PENDING_TASK[task_id]['cost']
        timeout = PENDING_TASK[task_id]['timeout']
        datahash = PENDING_TASK[task_id]['datahash']
        code_bin = PENDING_TASK[task_id]['code_bin']
    else:
        print('DataHash Not Found in Routing Node')
        return 'None'

    computer_id = search_for_available_computer()

    data_link = get_data_link(datahash)

    UNDER_MY_WORKING.add(computer_id)
    computer_address = give_me_computer_address(computer_id)
    computer_address += '/new_task/'
    computer_address += str(MY_ID)

    MY_TASK.insert(task_id, [data_user_id, computer_id, give_me_time_counter(), datahash, cost, timeout, code_bin])

    if task_id in PENDING_TASK:
        PENDING_TASK.pop(task_id)

    try:
        requests.post(computer_address, data = {'task_id' : str(task_id), 'datahash' : datahash, 'data_link' : str(data_link)})
    except:
        MY_TASK.pop(task_id)
        new_task(data_user_id, task_id)
        return

    FP.write(give_me_time() + 'ROUTER ' + str(MY_ID) + ' Assigning task id ' + str(task_id) + ' to computer id ' + str(computer_id) + '\n')
    
    routers = give_me_random_routers(computer_id)
    
    for router in routers:
        router_address = give_me_router_address(router)
        router_address += '/computer/work/'
        router_address += str(computer_id)
        requests.post(router_address)

    computer_address = give_me_computer_address(computer_id)
    computer_address += '/goto_work'

    requests.post(computer_address, data = {'code_bin' : str(code_bin), 'task_id' : task_id})

    return str(computer_id)
    

def end_task(task_id, return_value, notify_data_user = True):

    global UNDER_MY_WORKING, MY_TASK

    record = MY_TASK.give_me_elem(task_id)

    computer_id = record[0]['computer_id']
    data_user_id = record[0]['data_user_id']
    cost = record[0]['cost']
    timeout = record[0]['timeout']
    datahash = record[0]['datahash']
    code_bin = record[0]['code_bin']

    UNDER_MY_WORKING.remove(computer_id)

    if not notify_data_user:
        PENDING_TASK[task_id] = {'data_user_id' : data_user_id, 'cost' : cost, 'timeout' : timeout, 'datahash' : datahash, 'code_bin' : code_bin}

    MY_TASK.pop(task_id)

    FP.write(give_me_time() + 'ROUTER ' + str(MY_ID) + ' Ending task id ' + str(task_id) + ' from computer id ' + str(computer_id) + '\n')
    
    routers = give_me_random_routers(computer_id)
    
    for router in routers:
        router_address = give_me_router_address(router)
        router_address += '/computer/finish/'
        router_address += str(computer_id)
        requests.post(router_address)

    if notify_data_user:
        #data_user_address = give_me_data_user_address(data_user_id)
        #data_user_address += '/end_task'
        #requests.post(data_user_address, data = {'task_id' : str(task_id), 'return_value' : str(return_value)})
        fp = open('Test Files/task_id_' + str(task_id) + '.txt', 'w')
        fp.write(return_value)
        fp.close()

def reassign_task(computer_id, data_user_id, task_id):
    FP.write(give_me_time() + 'ROUTER ' + str(MY_ID) + ' Reassigning task id ' + str(task_id) + '\n')
    
    end_task(task_id, 'nothing', False)
    new_task(data_user_id, task_id)

def check_working_computers():

    while True:
        for record in MY_TASK.iteritems():
            task_id = record['task_id']
            now_time = give_me_time_counter()
            if now_time - record['heartbeat'] > WORKING_COMPUTER_DETECTION_TIME:
                reassign_task(record['computer_id'], record['data_user_id'], task_id)

        time.sleep(WORKING_COMPUTER_DETECTION_TIME)

def run(my_id):
    init(my_id)
    thread.start_new_thread(delete_expired_heartbeat, ())
    thread.start_new_thread(check_working_computers, ())
    while True:
        time.sleep(1000)
