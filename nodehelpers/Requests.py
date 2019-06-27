import httplib, urllib

class response(object):

    def __init__(self, text):
        self.text = text

def get(address = '', _timeout = 300):
    address = address[7:]
    ind = address.find('/')
    if(ind == -1):
        address += '/'
        ind = len(address) - 1

    http_server = address[:ind]
    address = address[ind:]

    conn = httplib.HTTPConnection(http_server, timeout = _timeout)
    conn.request('GET', address)

    rsp = conn.getresponse()

    ret = str(rsp.read())

    conn.close()

    return response(ret)

def post(address = '', data = {}, _timeout = 300):
    address = address[7:]
    ind = address.find('/')
    if(ind == -1):
        address += '/'
        ind = len(address) - 1

    http_server = address[:ind]
    address = address[ind:]

    conn = httplib.HTTPConnection(http_server, timeout = _timeout)

    params = urllib.urlencode(data)
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

    conn.request('POST', address, params, headers)
    rsp = conn.getresponse()

    ret = str(rsp.read())

    conn.close()

    return response(ret)