import sys 
sys.path.append('..')

from AES.AESCipher import AESCipher 
import httplib, urllib 
import json 
from Crypto.PublicKey import RSA 
from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS1_v1_5 
import base64, os 
from urlparse import urlparse 
import uuid 
from collections import OrderedDict 

MAX_ALLOWED_SESSION = 500 

DEBUG = False 

class covatls(object): 
    def __init__(self): 
        super(covatls, self).__init__() 
        self.session_id = None 
        self.session_key = None 
        self.session_dict = OrderedDict() 

    def get_host_length(self, address): 
        ln = len(address) 

        for i in range(ln): 
            if address[i] == '/': 
                return i + 1 

    def reform_address(self, address): 
        if len(address)>0 and address[0] == '/': 
            address = address[1:] 

        if len(address)>0 and address[-1] == '/': 
            address = address[0:-1] 

        return address 

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

    def handle_session(self, host, session_id): 
        if session_id != None: 
            if session_id in self.session_dict: 
                self.session_id = session_id 
                self.session_key = self.session_dict[self.session_id] 
                del self.session_dict[self.session_id] 
                self.session_dict[self.session_id] = self.session_key 
                return True 

            else: 
                self.response = "Invalid Session ID" 
                return False 

        elif self.make_session(host) != True: 
            response = {} 
            response["error"] = True 
            response["description"] = "Failed to resolve challenge" 
            self.response = response 
            return False 

        return True 

    def split_url(self, address): 
        if len(address)>7 and address[0:7] == "http://": 
            address = address[7:] 

        host_len = self.get_host_length(address) 
        return (self.reform_address(address[0:host_len]), self.reform_address(address[host_len:])) 

    def reset_session(self): 
        self.session_id = None 
        self.session_key = None 

    def make_challenge(self, public_key): 
        keyPub = RSA.importKey(public_key) 
        cipher = Cipher_PKCS1_v1_5.new(keyPub) 
        self.session_key = str(uuid.uuid4().hex)
        if DEBUG:
            print("session key", self.session_key) 

        encrypted_challenge = cipher.encrypt(self.session_key.encode()) 
        converted_challenge = base64.b64encode(encrypted_challenge) 
        return str(converted_challenge)  

    def send_challenge(self, address, challenge): 
        conn = httplib.HTTPConnection(address) 
        data = dict() 
        data["challenge"] = challenge 
        json_data = json.dumps(data) 

        post_data = {"data" : json_data}
        params = urllib.urlencode(post_data) 
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
        conn.request("POST", "/cova_tls_session/challenge", params, headers) 
        response = conn.getresponse() 
        response_data = response.read() 
        conn.close() 

        return response_data 

    def validate_challenge(self, address, public_key): 
        challenge = self.make_challenge(public_key) 

        if DEBUG:
            print(type(challenge), challenge) 

        response_data = self.send_challenge(address, challenge) 

        if DEBUG:
            print("got response",response_data) 

        decrypted_data = self.decrypt(response_data) 
        challenge_ans = json.loads(decrypted_data) 

        if self.session_key == challenge_ans["challenge"]: 
            self.session_id = str(challenge_ans["session_id"] ) 
            self.session_dict[self.session_id] = self.session_key 

            if len(self.session_dict) > MAX_ALLOWED_SESSION: 
                self.session_dict.popitem(last=False) 

            return True 

        return False 

    def make_session(self, address): 
        if DEBUG:
            print("client", address) 

        conn = httplib.HTTPConnection(address) 
        conn.request("GET", "/cova_tls_session/create") 
        response = conn.getresponse() 
        key_value = json.loads(response.read()) 
        public_key = key_value["pub_key"] 
        conn.close() 
        return self.validate_challenge(address, public_key) 

    def get(self, address, session_id = None): 
        if session_id == None: 
            self.reset_session() 

        (host, access_path) = self.split_url(address)

        if self.handle_session(host, session_id) == False: 
            return self.response 

        conn = httplib.HTTPConnection(host) 
        conn.request("GET", str(self.hex_encrypt(access_path) + "/cova_tls_session_id/" + self.session_id))
        res = conn.getresponse() 
        response_data = str(res.read()) 
        return self.decrypt(response_data) 

    def post(self, address, data, session_id = None): 
        if session_id == None: 
            self.reset_session() 

        if isinstance(data,dict) == False: 
            return "Data must be dictionary type" 

        (host, access_path) = self.split_url(address)

        if self.handle_session(host, session_id) == False: 
            return self.response 

        json_data = json.dumps(data) 
        enc_json_data = self.encrypt(json_data) 
        post_data = {"data" : enc_json_data} 
        params = urllib.urlencode(post_data)
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"} 
        conn = httplib.HTTPConnection(host) 
        conn.request("POST", str(self.hex_encrypt(access_path) + "/cova_tls_session_id/" + self.session_id), params, headers) 
        response = conn.getresponse() 
        return self.decrypt(response.read()) 
