import nacl.secret
import nacl.utils
import binascii
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

def decrypt_data(encrypted_data, key):
    hashFunction = nacl.secret.SecretBox(key)

    #try:
    decrtpted_data = hashFunction.decrypt(encrypted_data)

    #except Exception as error:
        #return "Invalid Key"

    return decrtpted_data

def decrypt_data_from_hexKey(encrypted_data, skey):
    key = binascii.unhexlify(skey)
    
    return decrypt_data(encrypted_data,key)

def get_data_from_url(download_link):
    import urllib2
    response = urllib2.urlopen(download_link)
    data = response.read()
    return data

def get_data(download_link, skey):
    return decrypt_data_from_hexKey(get_data_from_url(download_link), skey)