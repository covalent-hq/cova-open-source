import os
from hashlib import sha256

class FileSaveHandler(object):
    def __init__(self):
        self.DEFAULT_DIR = os.getcwd()

    def save_file(self,data,path):
        encrypted_file_path = path + "/" + sha256(data).hexdigest() + '.enc'

        with open(encrypted_file_path, "wb+") as fileWrite:
            fileWrite.write(data)

    def save_secrets(self,data,path):
        encrypted_file_path = path + "/" + sha256(data).hexdigest() + 'Secrets.enc'

        with open(encrypted_file_path, "wb+") as fileWrite:
            fileWrite.write(data)

    def save_file_with_secrets(self, enc_data, secrets, path):
        hashValue = sha256(enc_data).hexdigest()
        encrypted_file_path = path + "/" + hashValue + ".enc"
        key_file_path = path + "/" + hashValue + "_key.enc"
        with open(encrypted_file_path, "wb+") as fileWrite:
            fileWrite.write(enc_data)

        with open(key_file_path, "wb+") as fileWrite:
            fileWrite.write(secrets)

        return hashValue 

    