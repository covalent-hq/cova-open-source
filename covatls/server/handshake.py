import os, base64 
from Crypto.PublicKey import RSA 
from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS1_v1_5 
import uuid 

class Handshake(object): 

    def __init__(self, session_key_pair, key_path, session_id = None): 
        super(Handshake, self).__init__() 

        self.session_id = session_id  
        self.session_key_pair = session_key_pair 
        self.key_path = key_path 

    def generate_session_id(self): 
        uid = uuid.uuid4() 
        return str(uid.hex) 
    
    def get_active_session_key(self): 
        return self.session_key_pair[self.session_id] 

    def read_key(self):
        with open(self.key_path) as file: 
            return file.read() 

    def solve_challenge(self, challenge): 
        private_key = None 
        private_key_path = self.key_path[0:-4] 

        with open(private_key_path) as file: 
            private_key = file.read() 

        keyPriv = RSA.importKey(private_key) 
        cipher = Cipher_PKCS1_v1_5.new(keyPriv) 
        converted_challenge = base64.b64decode(challenge)
        decrypt_text = cipher.decrypt(converted_challenge, None).decode() 
        decrypt_text = str(decrypt_text) 
        return decrypt_text 
        

    def create_session(self): 
        public_key = self.read_key() 
        data = {"pub_key" : public_key} 
        return data 
