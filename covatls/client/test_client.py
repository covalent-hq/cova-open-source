from cova_client_request import covatls 

class Test(object): 
    def __init__(self): 
        super(Test,self).__init__() 
        self.conn = covatls() 
    
    def test1(self): 
        res = self.conn.get("http://127.0.0.1:8080/new_task/1") 
        self.test1_session = self.conn.session_id 

        if res == 'my_func' :
            print("test1 Passed") 

        else: 
            print("test1 doesn't match") 

    def test2(self): 
        data = {"mottakin_bhai" : "BOSS"} 
        res = self.conn.post("http://127.0.0.1:8080/new_task/1", data) 
        self.test2_session = self.conn.session_id 

        if res == 'Pmy_func BOSS' :
            print("test2 Passed") 

        else: 
            print("test2 doesn't match") 

    def test3(self): 
        res = self.conn.get("http://127.0.0.1:8080/init_task/1/2", self.test2_session) 
        
        if res == 'my_func2' :
            print("test3 Passed") 

        else: 
            print("test3 doesn't match") 

    def test4(self): 
        data = {"mottakin_bhai" : " BOSS"} 
        res = self.conn.post("http://127.0.0.1:8080/init_task/1/2/", data, self.test1_session) 

        if res == 'Pmy_func2 BOSS' :
            print("test4 Passed") 

        else: 
            print("test4 doesn't match") 

    def run(self): 
        self.test1() 
        self.test2() 
        self.test3() 
        self.test4() 

obj = Test() 
obj.run()     
