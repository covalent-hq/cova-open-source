import time, thread, sys, requests
import data_user_protocol
from datetime import datetime
import request_helper

def hello():
    return 'Data User : Hello, World at port ' + sys.argv[1]

def init_task(router_id, form):
    return data_user_protocol.init_task(str(router_id), int(form['timeout']), str(form['datahash']), str(form['code_bin']))

def new_task(task_id, router_id):
    computer_id = data_user_protocol.new_task(str(task_id), str(router_id))
    return str(computer_id)

def start_task(form):
    data_user_protocol.start_task(str(form['code_bin']), str(form['task_id']), str(form['computer_id']))
    return 'something'

def restart_task(form):
    data_user_protocol.restart_task(str(form['task_id']))
    return 'restarted task'

def end_task(form):
	return data_user_protocol.end_task(str(form['task_id']), str(form['return_value']))

def get_all_task():
	return data_user_protocol.print_all_task()

get_req = {'hello' : ['/', 0],
           'new_task' : ['/new_task', 2],
           'get_all_task' : ['/get_all_task', 0]}
post_req = {'init_task' : ['/init_task', 1],
            'start_task' : ['/start_task', 0],
            'restart_task' : ['/restart_task', 0],
            'end_task' : ['/end_task', 0]}

request_helper.hello = hello
request_helper.new_task = new_task
request_helper.get_all_task = get_all_task
request_helper.init_task = init_task
request_helper.start_task = start_task
request_helper.restart_task = restart_task
request_helper.end_task = end_task

def init():
    data_user_protocol.run(str(sys.argv[1]))

def flaskThread():
    ob = request_helper.ManualRequest(get_req, post_req, int(sys.argv[1]))
    ob.run()
    
if __name__ == "__main__":
    thread.start_new_thread(flaskThread, ())
    thread.start_new_thread(init, ())
    while True:
        time.sleep(1000)
