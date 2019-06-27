import sys 
sys.path.append('..')
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import json 
from cgi import parse_header, parse_multipart 
from urlparse import parse_qs 
from SocketServer import ThreadingMixIn  
from collections import OrderedDict 
from handshake import Handshake 
from AES.AESCipher import AESCipher
import threading
from io import BytesIO 

DEBUG = False 
MAX_ALLOWED_SESSION = 500 

get_requests = dict()
post_requests = dict() 
session_db = OrderedDict() 
rsa_key_path = "id_rsa.pub"

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler): 

    def get_workable_path(self): 
        list_of_params = self.path.split('/')
        list_of_params = [x for x in list_of_params if x != ''] 
        total_params = len(list_of_params) 

        if len(list_of_params) > 1: 
            if list_of_params[-2] == "cova_tls_session" or list_of_params[-2] == "cova_tls_session_id": 
                actual_path = "" 

                for iterator in range(total_params-2): 
                    actual_path += "/"
                    actual_path += list_of_params[iterator] 

                session_path = "/" + list_of_params[-2] + "/" + list_of_params[-1]
            
            return (actual_path,session_path)
        
        return (self.path, "") 

    def generate_response(self, error_message): 
        if DEBUG: 
            print("response", error_message) 

        self.send_response(200)
        self.end_headers()
        self.wfile.write(error_message) 

    def get_challenge_response(self, challenge): 
        new_hand = Handshake(session_db, rsa_key_path, None) 
        solved_challenge = new_hand.solve_challenge(challenge) 
        session_id = new_hand.generate_session_id() 

        data = {"challenge" : solved_challenge, "session_id" : session_id} 
        session_db[session_id] = solved_challenge 
        self.session_key = solved_challenge 

        while len(session_db) > MAX_ALLOWED_SESSION: 
            session_db.popitem(last=False) 
        
        if DEBUG: 
            print("solved challenge", data) 

        return data 

    def initiate_session_key(self, session_id): 
        if DEBUG:
            print("session_id", session_id, session_db) 

        if session_id in session_db: 
            self.session_key = session_db[session_id] 
            del session_db[session_id] 
            session_db[session_id] = self.session_key 
            return True 

        else: 
            self.generate_response("Session ID doesn't exist in server")  
            return False 

    def handle_session(self, session_path, challenge = None): 
        session_params = session_path.split('/') 
        session_params = [x for x in session_params if x != ''] 

        if session_params[0] == "cova_tls_session": 
            if session_params[1] == "challenge": 
                challenge = json.loads(self.json_data) 
                data = self.get_challenge_response(challenge["challenge"]) 
                json_data = json.dumps(data) 
                self.generate_response(self.encrypt(json_data)) 
            
            elif session_params[1] == "create": 
                new_hand = Handshake(session_db, rsa_key_path, None) 
                session_info = new_hand.create_session() 
                self.generate_response(json.dumps(session_info)) 

            else: 
                self.generate_response("cova_tls_session error !!") 

            return False

        elif session_params[0] == "cova_tls_session_id": 
            return self.initiate_session_key(session_params[1]) 

        else: 
            self.generate_response("Session Error !!") 
            return False 

    def encrypt(self, message): 
        box = AESCipher(self.session_key, 16) 
        return str(box.encrypt(message)) 

    def decrypt(self, message): 
        box = AESCipher(self.session_key, 16) 
        return str(box.decrypt(message)) 

    def hex_encrypt(self, message): 
        box = AESCipher(self.session_key, 16) 
        return box.hex_encrypt(message) 

    def hex_decrypt(self, message): 
        box = AESCipher(self.session_key, 16) 
        return box.hex_decrypt(message) 

    def do_GET(self): 
        if DEBUG: 
            print(self.path) 
        
        (enc_path, session_path) = self.get_workable_path() 

        if len(session_path) == 0: 
            self.generate_response("Session ID Error !!")
            return

        else: 
            if self.handle_session(session_path) == False: 
                return 
 
        isExist = False 

        if DEBUG:
            print("session is established successfully") 
            print("enc_path", enc_path) 

        dec_path = self.hex_decrypt(enc_path[1:]) 
        path = "/" + dec_path 

        if DEBUG:
            print("decrypt path", path) 

        for fName in get_requests:
            details = get_requests[fName]
            ln = len(details[0])

            if details[0] == path[0:ln] :
                rest_of_url = path[ln+1:]
                list_of_params = rest_of_url.split('/')
                list_of_params = [x for x in list_of_params if x != ''] 

                if DEBUG:
                    print(len(list_of_params), list_of_params, details[1]) 

                if len(list_of_params) == details[1] :
                    isExist = True
                    func  = str(globals()[fName](*list_of_params))
                    self.send_response(200)
                    self.end_headers() 
                    encrypted_response = self.encrypt(func) 

                    if DEBUG: 
                        print(self.session_key, encrypted_response) 

                    self.wfile.write(encrypted_response) 
                    break

        if isExist == False:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(self.encrypt('No Such Route Exists !!')) 

    def parse_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        response = BytesIO()
        response.write(b'This is POST request. ')
        response.write(b'Received: ')
        fields = parse_qs(body)
        temp_keyPairs = {}

        for key, value in fields.iteritems():
            temp_keyPairs[key] = value[0] 

        if DEBUG:
            print("after parse", temp_keyPairs)

        return temp_keyPairs["data"] 

    def do_POST(self): 
        self.json_data = self.parse_POST()

        (enc_path, session_path) = self.get_workable_path() 

        if len(session_path) == 0: 
            self.generate_response("Session ID Error !!")
            return

        else: 
            if self.handle_session(session_path) == False: 
                return 

        if DEBUG:
            print("session is established successfully")
            print("enc_path", enc_path) 

        dec_path = self.hex_decrypt(enc_path[1:]) 
        path = "/" + dec_path 

        if DEBUG: 
            print("decrypt path",path)

        decrypted_data = self.decrypt(self.json_data) 
        keyPairs = json.loads(decrypted_data) 
        isExist = False 

        if DEBUG: 
            print("parsed data", keyPairs) 

        for fName in post_requests:
            details = post_requests[fName]
            ln = len(details[0])

            if details[0] == path[0:ln] :
                rest_of_url = path[ln+1:]
                list_of_params = rest_of_url.split('/') 
                list_of_params = [x for x in list_of_params if x != ''] 
                if len(list_of_params) == details[1] :
                    isExist = True
                    list_of_params.append(keyPairs)
                    func  = str(globals()[fName](*list_of_params)) 
                    encrypted_response = self.encrypt(func) 
                    self.wfile.write(encrypted_response) 
                    break 

        if isExist == False:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(self.encrypt('No Such Route Exists !!')) 

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

class ManualServer:
    def __init__(self, get_routes, post_routes, host, port_number):
        self.get_routes = get_routes 
        self.post_routes = post_routes 
        self.port_number = port_number 
        self.host = host 

    def run(self):
        global get_requests
        global post_requests    
        get_requests = self.get_routes
        post_requests = self.post_routes
        httpd = ThreadedHTTPServer((self.host, self.port_number), SimpleHTTPRequestHandler)
        httpd.serve_forever() 
