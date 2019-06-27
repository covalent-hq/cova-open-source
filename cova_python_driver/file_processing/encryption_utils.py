import nacl.secret
import nacl.utils
import base64
import json
from hashlib import sha256
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


# TODO: Make both hash computation and encryption chunked
def compute_sha256_hash(data):
    return sha256(data).hexdigest()


def compute_sha256_hash_file(filepath):
    fileRead = open(filepath,"rb")
    data = fileRead.read()

    return compute_sha256_hash(data)

def print_rand():
    print("this")

def encrypt_data(data):
    key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)

    hashFunction = nacl.secret.SecretBox(key)

    encrypted_data = hashFunction.encrypt(data)
    return encrypted_data,key

def encrypt_json_data(json_data):
    data = json_data.encode()
    encrypted_data,key = encrypt_data(data)
    return encrypted_data,key

def decrypt_data(data,key):
    hashFunction = nacl.secret.SecretBox(key)

    try:
        data = hashFunction.decrypt(data)

    except Exception as error:
        return "Invalid Key"

    return data

def encrypt_file(filepath, skey):

    with open(filepath, "rb") as fileRead:
        data = fileRead.read()

    key = sha256(str.encode(skey)).digest()

    hashFunction = nacl.secret.SecretBox(key)
    Rnonc = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)

    encrypted_data = hashFunction.encrypt(data, Rnonc, encoder=nacl.encoding.HexEncoder)

    encrypted_file_path = compute_sha256_hash(encrypted_data) + '.enc'

    with open(encrypted_file_path, "wb+") as fileWrite:
        fileWrite.write(encrypted_data)

    return encrypted_file_path, compute_sha256_hash(data), compute_sha256_hash(encrypted_data)


def decrypt_file(filepath, skey):

    with open(filepath, "rb") as fileRead:
        encrypted_data = fileRead.read()

    key = sha256(str.encode(skey)).digest()

    hashFunction = nacl.secret.SecretBox(key)

    try:
        data = hashFunction.decrypt(ciphertext=encrypted_data,encoder=nacl.encoding.HexEncoder)

    except Exception as error:
        return "Invalid Key"

    return data, compute_sha256_hash(data), compute_sha256_hash(encrypted_data)


def decrypt_file_as_df(filepath, skey):
    import pandas as pd
    
    data, _, _ = decrypt_file(filepath, skey)

    return pd.read_csv(StringIO(data))
    