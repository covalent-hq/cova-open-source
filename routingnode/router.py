import time, threading, sys
import router_protocol
from nodehelpers import request_helper
from nodehelpers.address_helper import *

def hello():
    return 'Router : Hello, World at port ' + router_protocol.MY_ID

def heartbeat_from_computer(computer_id, form):
    router_protocol.process_heartbeat(str(computer_id), int(form['localtime']))
    return "Got Heartbeat"

def heartbeat_from_working_computer(computer_id, form):
    router_protocol.process_working_heartbeat(str(computer_id), int(form['localtime']), str(form['task_id']))
    return "Got Heartbeat"

def start_working_post(computer_id, form):
    router_protocol.make_computer_unavailable(str(computer_id))
    return 'Computer is unavailable : ' + str(computer_id)

def finish_working_post(computer_id, form):
    router_protocol.make_computer_available(str(computer_id))
    return 'Computer is available : ' + str(computer_id)

def allstatus():
    return router_protocol.return_all_status()

def init_task(data_user_id, form):
    return router_protocol.init_task(str(data_user_id), int(form['timeout']), str(form['datahash']), str(form['code_bin']))

def new_task(data_user_id, form):
    computer_id = router_protocol.new_task(str(data_user_id), str(form['task_id']))
    return str(computer_id)

def end_task(form):
    router_protocol.end_task(str(form['task_id']), str(form['return_value']))
    return 'Ended Task'

def search_available(form):
    return str(router_protocol.give_me_available_computer())

def dec_key_fragment(form):
    print('Got It in dec key')
    return router_protocol.dec_key_fragment(str(form['datahash']))

def join_req(computer_id, form):
    router_protocol.join_req(str(computer_id), str(form['address']), str(form['region']), int(form['power']))
    return 'joined'

def give_me_result(task_id):
    return router_protocol.give_me_result(str(task_id))

def status_ok():
    return 'success'

get_req = {'hello' : ['/', 0],
           'allstatus' : ['/allstatus', 0],
           'give_me_result' : ['/give_me_result', 1],
           'status_ok' : ['/status_ok', 0]}
post_req = {'heartbeat_from_computer' : ['/computer/heartbeat', 1],
            'heartbeat_from_working_computer' : ['/computer/workingheartbeat', 1],
            'start_working_post' : ['/computer/work', 1],
            'finish_working_post' : ['/computer/finish', 1],
            'init_task' : ['/data_user/init_task', 1],
            'new_task' : ['/data_user/new_task', 1],
            'end_task' : ['/computer/end_task', 0],
            'search_available' : ['/search_available', 0],
            'dec_key_fragment' : ['/dec_key_fragment', 0],
            'join_req' : ['/join_req', 1]}

request_helper.hello = hello
request_helper.allstatus = allstatus
request_helper.heartbeat_from_computer = heartbeat_from_computer
request_helper.heartbeat_from_working_computer = heartbeat_from_working_computer
request_helper.start_working_post = start_working_post
request_helper.finish_working_post = finish_working_post
request_helper.init_task = init_task
request_helper.new_task = new_task
request_helper.end_task = end_task
request_helper.search_available = search_available
request_helper.dec_key_fragment = dec_key_fragment
request_helper.join_req = join_req
request_helper.give_me_result = give_me_result
request_helper.status_ok = status_ok

def init(my_id, cred):
    router_protocol.run(my_id, cred)

def flaskThread(my_id):
    address = ROUTER_ADDRESS[my_id]['public_ip']
    port = get_port(address)
    ob = request_helper.ManualRequest(get_req, post_req, port)
    ob.run()
    
def run(my_id, cred):
    threading.Thread(target = flaskThread, args = (my_id, )).start()
    threading.Thread(target = init, args = (my_id, cred, )).start()
    while True:
        time.sleep(1000)
