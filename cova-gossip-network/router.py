import time, thread, sys
import router_protocol
import request_helper

def hello():
    return 'Router : Hello, World at port ' + sys.argv[1]

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

def join_req(computer_id):
    router_protocol.join_req(str(computer_id))
    return 'joined'

get_req = {'hello' : ['/', 0],
           'allstatus' : ['/allstatus', 0],
           'join_req' : ['/join_req', 1]}
post_req = {'heartbeat_from_computer' : ['/computer/heartbeat', 1],
            'heartbeat_from_working_computer' : ['/computer/workingheartbeat', 1],
            'start_working_post' : ['/computer/work', 1],
            'finish_working_post' : ['/computer/finish', 1],
            'init_task' : ['/data_user/init_task', 1],
            'new_task' : ['/data_user/new_task', 1],
            'end_task' : ['/computer/end_task', 0],
            'search_available' : ['/search_available', 0],
            'dec_key_fragment' : ['/dec_key_fragment', 0]}

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

def init():
    router_protocol.run(str(sys.argv[1]))

def flaskThread():
    ob = request_helper.ManualRequest(get_req, post_req, int(sys.argv[1]))
    ob.run()
    
if __name__ == "__main__":
    thread.start_new_thread(flaskThread, ())
    thread.start_new_thread(init, ())
    while True:
        time.sleep(1000)
