import time, threading, json, random, hashlib, string

from collections import deque
from datetime import datetime
from sets import Set
import decrypt_key

from nodehelpers import database_helper
from nodehelpers import Requests as requests
from configs.config_loader import load_config
from configs.protocol_const import *
from nodehelpers.address_helper import *
from logger import log_helper


MY_ID = 0
AVAILABILITY_LIST = {}
AVAILABLE_COMPUTERS_DEQUE = database_helper.MemoryQueue('Available_Computer', ['computer_id', 'localtime'])
MY_TASK = database_helper.MemoryDict('My_Task', 'task_id', ['data_user_id', 'computer_id', 'heartbeat', 'datahash', 'cost', 'timeout', 'code_bin'])
FP = 0
PENDING_TASK = {}
CREDENTIALS = {}
RESULT = {}

heartbeat_lock = threading.Lock()
task_lock = threading.Lock()

def give_me_result(task_id):
    if task_id not in RESULT:
        return 'Result Not Found'

    ret = RESULT[task_id]

    RESULT.pop(task_id)

    return ret

def give_me_computer_address(computer_id):
    global AVAILABILITY_LIST
    return 'http://' + AVAILABILITY_LIST[computer_id]['address']

def join_req(computer_id, address, region, power):
    global AVAILABILITY_LIST
    AVAILABILITY_LIST[computer_id] = {'availability' : True, 'address' : address, 'region' : region, 'power' : power}

def init(my_id, cred):
    global MY_ID, FP, CREDENTIALS
    MY_ID = my_id
    FP = open('Log/' + str(MY_ID) + '.txt', 'w+', 0)
    
    CREDENTIALS = cred
    log_helper.init(my_id)

def make_computer_available(computer_id):
    global AVAIBILITY_LIST
    AVAILABILITY_LIST[computer_id]['availability'] = True
    
def make_computer_unavailable(computer_id):
    global AVAIBILITY_LIST
    AVAILABILITY_LIST[computer_id]['availability'] = False

def process_heartbeat(computer_id, localtime):
    global AVAILABLE_COMPUTERS_DEQUE
    FP.write(give_me_time() + ' Got Heartbeat from ' + str(computer_id) + '\n')

    heartbeat_lock.acquire()
    AVAILABLE_COMPUTERS_DEQUE.push([computer_id, give_me_time_counter()])
    heartbeat_lock.release()

    log_helper.add_heartbeat(computer_id, AVAILABILITY_LIST[computer_id]['region'], AVAILABILITY_LIST[computer_id]['power'])

def process_working_heartbeat(computer_id, localtime, task_id):
    global MY_TASK

    FP.write(give_me_time() + ' Got Working Heartbeat from ' + str(computer_id) + '\n')

    task_lock.acquire()

    if MY_TASK.is_in(task_id):
        record = MY_TASK.give_me_elem(task_id)
        record[0]['heartbeat'] = give_me_time_counter()

    task_lock.release()

def delete_expired_heartbeat():
    global AVAILABLE_COMPUTERS_DEQUE
    while True:
        heartbeat_lock.acquire()

        while not AVAILABLE_COMPUTERS_DEQUE.is_empty():
            now_heartbeat = AVAILABLE_COMPUTERS_DEQUE.top()
            if int(time.mktime(datetime.now().timetuple())) - now_heartbeat['localtime'] > HEARTBEAT_CLEAR_TIME:
                AVAILABLE_COMPUTERS_DEQUE.pop()
                log_helper.remove_heartbeat(now_heartbeat['computer_id'])
            else:
                break

        heartbeat_lock.release()

        time.sleep(2)

def give_me_available_computer():
    global AVAILABLE_COMPUTERS_DEQUE

    heartbeat_lock.acquire()

    while not AVAILABLE_COMPUTERS_DEQUE.is_empty():
        now_heartbeat = AVAILABLE_COMPUTERS_DEQUE.top()

        if AVAILABILITY_LIST[now_heartbeat['computer_id']]['availability']:
            heartbeat_lock.release()
            return now_heartbeat['computer_id']

        AVAILABLE_COMPUTERS_DEQUE.pop()

        log_helper.remove_heartbeat(now_heartbeat['computer_id'])

    heartbeat_lock.release()

    return None

def search_for_available_computer():

    computer_id = 'None'

    start_time = time.time()

    while True:

        if(time.time() - start_time > SEARCH_TIME):
            return 'None'

        random_router_id = random.randint(0, NUMBER_OF_ROUTERS - 1)
        random_router_id = 'router' + str(random_router_id)
        router_address = give_me_router_address(str(random_router_id))
        router_address += '/search_available'
        try:
            computer_id = str(requests.post(router_address).text)
        except:
            continue
        if computer_id not in AVAILABILITY_LIST:
            continue
        return str(computer_id)

def task_id_generator():
    letters = string.ascii_lowercase
    random_string = str(int(time.time()))
    random_string += ''.join(random.choice(letters) for i in range(3))
    return random_string

def cost_function(timeout):
    return 5

def init_task(data_user_id, timeout, datahash, code_bin):

    if timeout > MAX_TIMEOUT:
        return json.dumps({'task_id' : 'Max Timeout Exceeded', 'cost' : 10000000000})

    global PENDING_TASK
    task_id = task_id_generator()

    cost = cost_function(timeout)

    PENDING_TASK[task_id] = {'data_user_id' : data_user_id, 'cost' : cost, 'timeout' : timeout, 'datahash' : datahash, 'code_bin' : code_bin}

    print(PENDING_TASK)

    return json.dumps({'task_id' : task_id, 'cost' : cost})

def check_for_agreement(data_user_id, task_id):

    global PENDING_TASK

    task_lock.acquire()

    if MY_TASK.is_in(task_id):
        task_lock.release()
        return True

    task_lock.release()

    if task_id not in PENDING_TASK:
        print('Task Id Is not in Pending Task')
        return False

    if LOCAL:
        return True

    address = ETH_API_ENDPOINT + '/payment/seeAgreement/' + task_id

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

    address = BDB_API_ENDPOINT + '/get_keyfrag/' + str(datahash) + '/' + str(MY_ID)

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

    address = BDB_API_ENDPOINT + '/get_keyfrag/' + str(datahash) + '/' + str(MY_ID)

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

    try:
        private_key = str(CREDENTIALS['rsa_cred']['privateKey'])
    except:
        print('Private Key Parsing Error')
        return datahash + str(MY_ID)

    try:
        ret = str(decrypt_key.decrypt_message(ret, private_key))
    except:
        print('Decryption Error')
        return datahash + str(MY_ID)

    return ret

def new_task(data_user_id, task_id):

    if not check_for_agreement(data_user_id, task_id):
        return 'None'

    global MY_TASK, PENDING_TASK, AVAILABILITY_LIST

    task_lock.acquire()

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
        task_lock.release()
        return 'None'

    task_lock.release()

    computer_id = search_for_available_computer()

    if(computer_id == 'None'):
        return 'No Computer Available. Network is congested.'

    data_link = get_data_link(datahash)

    computer_address = give_me_computer_address(computer_id)
    computer_address += '/new_task/'
    computer_address += str(MY_ID)

    task_lock.acquire()

    MY_TASK.insert(task_id, [data_user_id, computer_id, give_me_time_counter(), datahash, cost, timeout, code_bin])

    task_lock.release()

    if task_id in PENDING_TASK:
        PENDING_TASK.pop(task_id)

    try:
        ret = str(requests.post(computer_address, data = {'task_id' : str(task_id), 'datahash' : datahash, 'data_link' : str(data_link), 'timeout' : str(timeout), 'code_bin' : str(code_bin)}).text)
        if ret != 'allright':
            print(give_me_time() + ' Already assigned work at ' + str(computer_id))
            raise Exception('Error')
    except:
        task_lock.acquire()
        MY_TASK.pop(task_id)
        task_lock.release()
        new_task(data_user_id, task_id)
        return

    FP.write(give_me_time() + 'ROUTER ' + str(MY_ID) + ' Assigning task id ' + str(task_id) + ' to computer id ' + str(computer_id) + '\n')

    log_helper.add_heartbeat(computer_id, AVAILABILITY_LIST[computer_id]['region'], AVAILABILITY_LIST[computer_id]['power'], True, task_id)
    log_helper.start_task_id(task_id, computer_id)
    
    routers = give_me_random_routers(computer_id)
    
    for router in routers:
        router_address = give_me_router_address(router)
        router_address += '/computer/work/'
        router_address += str(computer_id)
        try:
            requests.post(router_address)
        except:
            print('Could not make computer ' + str(computer_id) + ' unavailable at ' + str(router))

    computer_address = give_me_computer_address(computer_id)
    computer_address += '/goto_work'

    return str(computer_id)
    

def end_task(task_id, return_value, notify_data_user = True):

    global MY_TASK, CREDENTIALS

    task_lock.acquire()

    if not MY_TASK.is_in(task_id):
        task_lock.release()
        return

    record = MY_TASK.give_me_elem(task_id)

    computer_id = record[0]['computer_id']
    data_user_id = record[0]['data_user_id']
    cost = record[0]['cost']
    timeout = record[0]['timeout']
    datahash = record[0]['datahash']
    code_bin = record[0]['code_bin']

    if not notify_data_user:
        PENDING_TASK[task_id] = {'data_user_id' : data_user_id, 'cost' : cost, 'timeout' : timeout, 'datahash' : datahash, 'code_bin' : code_bin}

    MY_TASK.pop(task_id)

    task_lock.release()

    FP.write(give_me_time() + 'ROUTER ' + str(MY_ID) + ' Ending task id ' + str(task_id) + ' from computer id ' + str(computer_id) + '\n')

    log_helper.remove_heartbeat(computer_id, True)
    
    log_helper.end_task_id(task_id, computer_id)
    
    routers = give_me_random_routers(computer_id)
    
    for router in routers:
        router_address = give_me_router_address(router)
        router_address += '/computer/finish/'
        router_address += str(computer_id)
        try:
            requests.post(router_address)
        except:
            print('Could not make computer ' + str(computer_id) + ' available at ' + str(router))

    if notify_data_user:
        #data_user_address = give_me_data_user_address(data_user_id)
        #data_user_address += '/end_task'
        #requests.post(data_user_address, data = {'task_id' : str(task_id), 'return_value' : str(return_value)})
        fp = open('Log/task_id_' + str(task_id) + '.txt', 'w')
        fp.write(return_value)
        fp.close()

        global RESULT

        RESULT[task_id] = return_value

        address = BDB_API_ENDPOINT + '/register_task'

        try:
            requests.post(address, data = {'bdb_public_key' : CREDENTIALS['bdb_cred']['publicKey'], 'bdb_private_key' : CREDENTIALS['bdb_cred']['privateKey'], 'task_id' : task_id})
        except:
            print('Could Not Update in bigchaindb')

def reassign_task(computer_id, data_user_id, task_id):
    FP.write(give_me_time() + 'ROUTER ' + str(MY_ID) + ' Reassigning task id ' + str(task_id) + '\n')

    print('Reassigning Task : ' + str(computer_id) + '  ' + str(task_id))
    
    end_task(task_id, 'nothing', False)
    new_task(data_user_id, task_id)

def check_working_computers():

    while True:

        task_lock.acquire()

        now_task = MY_TASK.iteritems()

        task_lock.release()

        for record in now_task:

            task_id = record['task_id']
            computer_id = record['computer_id']
            data_user_id = record['data_user_id']
            heartbeat = record['heartbeat']

            now_time = give_me_time_counter()
            if now_time - heartbeat > WORKING_COMPUTER_DETECTION_TIME:
                reassign_task(computer_id, data_user_id, task_id)

        time.sleep(WORKING_COMPUTER_DETECTION_TIME)

def send_logger():
    while True:

        log_helper.print_to_logger()

        time.sleep(5)

def run(my_id, cred):
    init(my_id, cred)
    threading.Thread(target = delete_expired_heartbeat).start()
    threading.Thread(target = check_working_computers).start()
    threading.Thread(target = send_logger).start()
    while True:
        time.sleep(1000)
