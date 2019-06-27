import time, thread, sys, requests
import computer_protocol
from datetime import datetime
import request_helper

def hello():
    return 'Computer : Hello, World at port ' + sys.argv[1]

def new_task_post(router_id, form):
    computer_protocol.wait_for_work(str(router_id), str(form['task_id']), str(form['datahash']), str(form['data_link']))
    return 'waiting to work'

def goto_work(form):
    computer_protocol.goto_work(str(form['task_id']), str(form['code_bin']))
    return 'went to work'

get_req = {'hello' : ['/', 0]}
post_req = {'new_task_post' : ['/new_task', 1],
            'goto_work' : ['/goto_work', 0]}

request_helper.hello = hello
request_helper.new_task_post = new_task_post
request_helper.goto_work = goto_work

def init():
    computer_protocol.run(str(sys.argv[1]))

def flaskThread():
    ob = request_helper.ManualRequest(get_req, post_req, int(sys.argv[1]))
    ob.run()
    
if __name__ == "__main__":
    thread.start_new_thread(flaskThread, ())
    thread.start_new_thread(init, ())
    while True:
        time.sleep(1000)
