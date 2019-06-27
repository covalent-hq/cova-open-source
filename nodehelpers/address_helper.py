import hashlib
import time
import string
import random
import json
from datetime import datetime
from configs.config_loader import load_config
from configs.protocol_const import *


fp = open(load_config(PUBLIC_ROUTING_NODES_FP), 'r')
ROUTER_ADDRESS = json.loads(fp.read())
fp.close()

if DASHBOARD_LOGGING:
    fp = open(load_config(LOGGER_FP), 'r')
    data = json.loads(fp.read())
    DASHBOARD_COMPUTER_ADDRESS = data['DASHBOARD_COMPUTER_ADDRESS']
    DASHBOARD_TASK_ID_ADDRESS = data['DASHBOARD_TASK_ID_ADDRESS']
    fp.close()

def random_string():
    letters = string.ascii_lowercase
    random_string = ''.join(random.choice(letters) for i in range(10))
    return random_string

def give_me_random_routers(computer_id):

    random_router = []
    while len(random_router) < HEARTBEAT_ROUTER_COUNT:
        now_router = random.randint(0, NUMBER_OF_ROUTERS - 1)

        now_id = 'router' + str(now_router)

        if now_id in random_router:
            continue

        random_router.append(now_id)
    
    return random_router

def give_me_router_address(router_id):
    return 'http://' + str(ROUTER_ADDRESS[router_id]['public_ip'])

def give_me_time_counter():
    return int(time.mktime(datetime.now().timetuple()))

def give_me_time():
    nowtime = datetime.now()
    return str(nowtime.hour) + ':' + str(nowtime.minute) + ':' + str(nowtime.second) + ' '

def get_port(address):
    if IS_DOCKER:
        return DEFAULT_DOCKER_COVA_PORT
    else:
        return int(address[address.find(':') + 1 : ])
