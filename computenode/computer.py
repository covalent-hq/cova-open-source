import time, threading, sys
import computer_protocol
from datetime import datetime
from nodehelpers import request_helper
from nodehelpers.address_helper import get_port


def hello():
    return 'Computer : Hello, World at port ' + computer_protocol.MY_ID

def new_task_post(router_id, form):
    return computer_protocol.start_working(str(router_id), str(form['task_id']), str(form['datahash']), str(form['data_link']), str(form['timeout']), str(form['code_bin']))

def status_ok():
    return 'success'

get_req = {'hello' : ['/', 0],
           'status_ok' : ['/status_ok', 0]}
post_req = {'new_task_post' : ['/new_task', 1]}

request_helper.hello = hello
request_helper.new_task_post = new_task_post
request_helper.status_ok = status_ok

def init(my_id, address, region):
    computer_protocol.run(my_id, address, region)

def flaskThread(address):
    port = get_port(address)
    ob = request_helper.ManualRequest(get_req, post_req, port)
    ob.run()
    
def run(my_id, address, region):
    threading.Thread(target = flaskThread, args = (address, )).start()
    threading.Thread(target = init, args = (my_id, address, region, )).start()
    while True:
        time.sleep(1000)
