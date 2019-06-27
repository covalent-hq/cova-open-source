from protocol_const import *
import time, thread, importlib, json
from secretsharing import SecretSharer
import random
import Requests as requests
import file_decryption
from covavm import runner
import hashlib

HEARTBEAT_ROUTERS = []
MY_ID = 0
IS_WORKING = False
MY_TASK_ID = 0
FP = 9
MY_ROUTER_ID = 0
MY_DATAHASH = ""
MY_KEY_FRAGMENTS = []
MY_DATA_LINK = ""

def init(my_id):
    global MY_ID, HEARTBEAT_ROUTERS, IS_WORKING, FP
    IS_WORKING = False
    MY_ID = my_id
    HEARTBEAT_ROUTERS = give_me_random_routers(MY_ID)
    FP = open('Log/computer.txt', 'a+', 0)

    for router in range(NUMBER_OF_ROUTERS):
        router_address = give_me_router_address(str(router + 10000))
        router_address += '/join_req/'
        router_address += str(MY_ID)
        requests.get(router_address)

def send_heartbeat():
    while True:
        for router in HEARTBEAT_ROUTERS:
            router_address = give_me_router_address(router)
            if IS_WORKING:
                router_address += '/computer/workingheartbeat/'
            else:
                router_address += '/computer/heartbeat/'
            router_address += str(MY_ID)
            
            now_time = give_me_time_counter()
            
            if IS_WORKING:
                requests.post(router_address, data = {'localtime' : str(now_time), 'task_id' : str(MY_TASK_ID)})
            else:
                requests.post(router_address, data = {'localtime' : str(now_time)})
        
        time.sleep(COMPUTER_HEARTBEAT_TIME)

def give_me_key_fragments(datahash):

    start_node = random.randint(0, NUMBER_OF_ROUTERS - 1)
    ret = []

    for i in range(SECRET_NUM):
        router_id = (start_node + i) % NUMBER_OF_ROUTERS

        router_id += 10000

        address = give_me_router_address(str(router_id))
        address += '/dec_key_fragment'
        dec_key_fragment = str(requests.post(address, data = {'datahash' : datahash}).text)
        ret.append(dec_key_fragment)

    return ret

def decrypt_secret(fragments):

    total_fragment = str(fragments[0]).count('^') + 1

    data = [[] for _ in range(total_fragment)]

    for line in fragments:
        temp = str(line).split('^')

        for i in range(total_fragment):
            data[i].append(temp[i])
       
    key = ""

    for i in range(total_fragment):
        tmp = SecretSharer.recover_secret(data[i])
        expected_length = 10
        if(i == total_fragment - 1):
            expected_length = 4

        tmp = "0" * (expected_length - len(tmp)) + tmp

        key += tmp

    return str(key)

def temp_working(code_bin):

    global MY_DATAHASH

    file_name = 'Code/code' + str(MY_ID) + '.py'
    code_fp = open(file_name, 'w+')
    code_fp.write(code_bin)
    code_fp.close()

    module_name = 'Code.code' + str(MY_ID)

    user_module = importlib.import_module(module_name)

    user_module.main()

    ret_fp = open('Code/output.txt', 'r')

    ret = ret_fp.read()

    ret += str('\n' + str(MY_DATAHASH))

    ret += str('\n' + str(MY_KEY_FRAGMENTS))

    ret += str('\n' + str(MY_DATA_LINK) + '\n')

    if not LOCAL:
        ret += str(decrypt_secret(MY_KEY_FRAGMENTS) + '\n')

    return ret

def ndarray_to_string(arr):

    return json.dumps(arr.tolist())

def working(code_bin):

    print(MY_KEY_FRAGMENTS)
    skey = decrypt_secret(MY_KEY_FRAGMENTS)

    print(MY_DATA_LINK)
    print(skey)

    data = file_decryption.get_data(MY_DATA_LINK, skey)

    print(data)

    data = json.loads(data)

    H = hashlib.md5(code_bin.encode()).hexdigest()

    print(H)

    print(data['policies'])

    ret = runner.run_with_covavm(code_bin, data['data'], data['policies'], ['__covaprogram__'])

    return ndarray_to_string(ret.payload)

def wait_for_work(router_id, task_id, datahash, data_link):
    global IS_WORKING, HEARTBEAT_ROUTERS, MY_TASK_ID, MY_ROUTER_ID, MY_DATAHASH, MY_KEY_FRAGMENTS, MY_DATA_LINK
    IS_WORKING = True
    MY_TASK_ID = task_id
    MY_ROUTER_ID = router_id
    MY_DATAHASH = datahash
    MY_DATA_LINK = data_link

    HEARTBEAT_ROUTERS = [router_id]

    MY_KEY_FRAGMENTS = give_me_key_fragments(datahash)
    MY_KEY_FRAGMENTS = [str(i) for i in MY_KEY_FRAGMENTS]

    FP.write(give_me_time() + 'COMPUTER ' + str(MY_ID) + ' Waiting task id ' + str(task_id) + ' from router id ' + str(router_id) + '\n')

def do_work(task_id, code):

    global IS_WORKING, HEARTBEAT_ROUTERS, MY_TASK_ID

    if(task_id != MY_TASK_ID):
        return

    FP.write(give_me_time() + 'COMPUTER ' + str(MY_ID) + ' Working task id ' + str(task_id) + '\n')

    if LOCAL:
        ret = temp_working(code)
    else:
        ret = working(code)

    FP.write(give_me_time() + 'COMPUTER ' + str(MY_ID) + ' Finished task id ' + str(task_id) + '\n')
    
    IS_WORKING = False
    HEARTBEAT_ROUTERS = give_me_random_routers(MY_ID)
    router_address = give_me_router_address(MY_ROUTER_ID)
    router_address += '/computer/end_task'
    requests.post(router_address, data = {'task_id' : str(task_id), 'return_value' : str(ret)})

def goto_work(task_id, code_bin):
    thread.start_new_thread(do_work, (task_id, code_bin))
    
def run(my_id):
    init(my_id)
    thread.start_new_thread(send_heartbeat, ())
    while True:
        time.sleep(1000)
