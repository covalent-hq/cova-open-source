import time, thread, json
from covatls.client.cova_client_request import covatls 

MY_ID = 0
MY_TASKS = {}
FP = 0

def init(my_id):
    global MY_ID, FP
    MY_ID = my_id
    FP = open('Log/data_user.txt', 'a+', 0)

def init_task(router, timeout, datahash, code, public_key, eth_address):
    router_address = router
    router_address += '/data_user/init_task/'
    router_address += str(eth_address)
    # tempData = {'timeout' : str(timeout), 'datahash' : datahash, 'code_bin' : code, 'public_key' : public_key}
    # print("------------ Asking routing nodes -----------", str(router_address), tempData)
    try:
        ret = covatls().post(str(router_address), data = {'timeout' : str(timeout), 'datahash' : datahash, 'code_bin' : code, 'public_key' : public_key})
    except Exception as err:
        print("error", err)
        raise err

    return json.loads(ret)

def new_task(task_id, router, asset_id, eth_address):
    router_address = router
    router_address += '/data_user/new_task/'
    router_address += str(eth_address)
    # print(asset_id)
    computer_id = str(covatls().post(router_address, data = {'task_id' : str(task_id), 'asset_id': asset_id}))
    
    if(computer_id == 'None'):
        return 'None'

    return str(computer_id)