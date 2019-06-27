import cova_server 

DEBUG = True 

def my_func(a): 
    if DEBUG: 
        print("get 1 ",a) 

    return str("my_func") 

def my_func2(a,b): 
    if DEBUG: 
        print("get 2",a,b) 

    return str("my_func2")

def Pmy_func(a,form): 
    if DEBUG: 
        print("post 1",a,form) 

    return str("Pmy_func " + form["mottakin_bhai"]) 

def Pmy_func2(a,b,form): 
    if DEBUG: 
        print("post 2",a,b,form) 

    return str("Pmy_func2" + form["mottakin_bhai"]) 

get_requests = {
    "my_func" : ["/new_task", 1] ,
    "my_func2" : ["/init_task", 2]
}

post_requests = {
    "Pmy_func" : ["/new_task", 1] ,
    "Pmy_func2" : ["/init_task", 2]
}

cova_server.my_func = my_func 
cova_server.my_func2 = my_func2 
cova_server.Pmy_func = Pmy_func 
cova_server.Pmy_func2 = Pmy_func2 

server = cova_server.ManualServer(get_requests, post_requests, '127.0.0.1', 8080) 
server.run() 