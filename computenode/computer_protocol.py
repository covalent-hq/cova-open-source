from nodehelpers import database_helper
from nodehelpers import Requests as requests
from covavm import runner
from configs.protocol_const import *
from nodehelpers.address_helper import *
from covathread import timeoutProcess

import time, threading, importlib, json
import random
import file_decryption
import hashlib
from secretsharingng.secret_utility import SecretRecoverer
import cpuinfo, copy

class Computer(object):

    def __init__(self, my_id):
        self.HEARTBEAT_ROUTERS = give_me_random_routers(my_id)
        self.ID = my_id
        self.IS_WORKING = False
        self.global_lock = threading.Lock()
        self.MY_TASK_ID = None

    def work_state(self, router_id, task_id):
        if self.IS_WORKING:
            return False
        self.HEARTBEAT_ROUTERS = [router_id]
        self.IS_WORKING = True
        self.MY_TASK_ID = task_id
        return True

    def lazy_state(self):

        self.HEARTBEAT_ROUTERS = give_me_random_routers(self.ID)
        self.IS_WORKING = False

    def read_routers(self):

        ret_routers = copy.deepcopy(self.HEARTBEAT_ROUTERS)
        ret_working = self.IS_WORKING

        return ret_routers, ret_working

    def is_working(self):

        return self.IS_WORKING

    def func_with_lock(self, fn, *args):
        self.global_lock.acquire()

        ret = fn(*args)

        self.global_lock.release()

        return ret

class Task(object):

    def __init__(self, task_id, router_id, datahash, data_link, timeout, code_bin):
        self.task_id = task_id
        self.router_id = router_id
        self.datahash = datahash
        self.data_link = data_link
        self.timeout = timeout
        self.code_bin = code_bin
        self.key_fragments = give_me_key_fragments(datahash)

    def working(self):

        global my_computer

        print(self.key_fragments)

        try:
            skey = decrypt_secret(self.key_fragments)
        except:
            print('Could not decrypt secret')
            return 'Could not decrypt secret'

        print(self.data_link)
        print(skey)

        try:
            data = file_decryption.get_data(self.data_link, skey)
        except:
            print('File Download and decryption Error')
            return 'File Download and decryption Error'

        print(data)

        data = json.loads(data)

        H = hashlib.md5(self.code_bin.encode()).hexdigest()

        print(H)

        print(data['policies'])

        ret = runner.run_with_covavm(self.code_bin, data['data'], data['policies'], ['__covaprogram__'])

        print(ret)

        try:
            return ndarray_to_string(ret.payload)

        except:
            return str(ret.payload)

    def end_protocol(self, ret):

        global my_computer

        print(give_me_time() + str(my_computer.ID) + ' Ending task ' + str(self.task_id))
        router_address = give_me_router_address(self.router_id)
        router_address += '/computer/end_task'
        try:
            requests.post(router_address, data = {'task_id' : str(self.task_id), 'return_value' : str(ret)})
        except:
            print(give_me_time() + str(my_computer.ID) + ' Error Sending return value of task ' + str(self.task_id) + ' to router ' + str(self.router_id))

    def do_work(self):

        ret = self.working()
        
        self.end_protocol(ret)

    def work_thread(self):

        global my_computer

        print(give_me_time() + 'Timeout : ' + str(self.timeout))

        prs = timeoutProcess(func = self.do_work, arguments = (), timeout = int(self.timeout))
        prs.startProcess().join()

        my_computer.func_with_lock(my_computer.lazy_state)

        if not prs.isFinished:
            print(give_me_time() + 'Time Limit Exceeded')
            self.end_protocol(self.task_id, 'Time Limit Exceeded')

    def run(self):
        print(give_me_time() + str(my_computer.ID) + ' starting task ' + str(self.task_id))
        threading.Thread(target = self.work_thread, args = ()).start()


my_computer = None

def init(my_id, my_address, region):
    global my_computer

    my_computer = Computer(my_id)

    power = cpuinfo.get_cpu_info()['hz_advertised_raw'][0] // 1000000

    #FP = open('Log/computer.txt', 'a+', 0)

    for router_address in ROUTER_ADDRESS:
        router_address = give_me_router_address(router_address)
        router_address += '/join_req/'
        router_address += str(my_computer.ID)
        print(router_address)
        try:
            requests.post(router_address, data = {'address' : my_address, 'region' : region, 'power' : power})
        except:
            print(give_me_time() + str(my_computer.ID) + ' Could not send init info to ' + str(router_address))

def send_heartbeat():
    while True:

        hrouters, is_working = my_computer.func_with_lock(my_computer.read_routers)

        for router in hrouters:

            router_address = give_me_router_address(router)

            if is_working:
                router_address += '/computer/workingheartbeat/'
            else:
                router_address += '/computer/heartbeat/'
            router_address += str(my_computer.ID)
            
            now_time = give_me_time_counter()

            try:
            
                if is_working:
                    print(give_me_time() + str(my_computer.ID) + ' sending working heartbeat to ' + str(router_address))
                    requests.post(router_address, data = {'localtime' : str(now_time), 'task_id' : str(my_computer.MY_TASK_ID)}, _timeout = 1)
                else:
                    print(give_me_time() + str(my_computer.ID) + ' sending heartbeat to ' + str(router_address))
                    requests.post(router_address, data = {'localtime' : str(now_time)}, _timeout = 1)
            except:
                print(give_me_time() + str(my_computer.ID) + ' Could not send heartbeat to router ' + str(router))
        
        time.sleep(COMPUTER_HEARTBEAT_TIME)

def give_me_key_fragments(datahash):

    start_node = random.randint(0, NUMBER_OF_ROUTERS - 1)
    ret = []

    counter = 0

    while True:
        router_id = (start_node + counter) % NUMBER_OF_ROUTERS

        router_id = 'router' + str(router_id)

        address = give_me_router_address(str(router_id))
        address += '/dec_key_fragment'

        try:
            dec_key_fragment = str(requests.post(address, data = {'datahash' : datahash}).text)
        except:
            print(give_me_time() + str(my_computer.ID) + ' Could not get key fragments')
            continue
        ret.append(str(dec_key_fragment))

        counter += 1

        if 2*counter > NUMBER_OF_ROUTERS:
            break

    return copy.deepcopy(ret)

def decrypt_secret(fragments):

    recoverer = SecretRecoverer(fragments)
    decrypted_key = recoverer.run()

    return str(decrypted_key)

def ndarray_to_string(arr):

    return json.dumps(arr.tolist())

def start_working(router_id, task_id, datahash, data_link, timeout, code_bin):
    print(give_me_time() + str(my_computer.ID) + ' Wait for work')

    available = my_computer.func_with_lock(my_computer.work_state, router_id, task_id)

    if not available:
        return 'not allright'

    job = Task(task_id, router_id, datahash, data_link, timeout, code_bin)

    job.run()

    #FP.write(give_me_time() + 'COMPUTER ' + str(MY_ID) + ' Waiting task id ' + str(task_id) + ' from router id ' + str(router_id) + '\n')

    return 'allright'
    
def run(my_id, my_address, region):
    init(str(my_id), str(my_address), str(region))
    threading.Thread(target = send_heartbeat).start()
    while True:
        time.sleep(1000)
