from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from Crypto import Random
from base64 import b64encode, b64decode

def importKey(externKey):
    return RSA.importKey(externKey)

def encrypt_pub(message, pub_key):
    cipher = PKCS1_OAEP.new( importKey(pub_key) )
    return b64encode(cipher.encrypt(message.encode()))

def encrypt_message(message,pub_key):
    total_len = len(message)
    encrypted_message = ""
    i = 0  

    while i < total_len:
        next_len = min(i + 70,total_len)
        encrypted_message += encrypt_pub(message[i:next_len],pub_key)
        i = next_len

    return encrypted_message

def decrypt_message(message, private_key):
    total_len = len(message)
    cipher = PKCS1_OAEP.new( importKey(private_key))
    decrypted_message = ""
    i = 0 

    while i<total_len:
        next_len = min(i + 172,total_len)
        decrypted_message += cipher.decrypt(b64decode(message[i:next_len]))
        i = next_len

    return decrypted_message