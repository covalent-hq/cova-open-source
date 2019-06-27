from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import json 
from cgi import parse_header, parse_multipart
from urlparse import parse_qs
from SocketServer import ThreadingMixIn
import threading

from io import BytesIO


# get_requests = {
#     "my_func" : ["/new_task", 1] ,
#     "my_func2" : ["/init_task", 2]
# }

# post_requests = {
#     "Pmy_func" : ["/new_task", 1] ,
#     "Pmy_func2" : ["/init_task", 2]
# }

get_requests = dict()

post_requests = dict()


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        path = self.path
        isExist = False

        for fName in get_requests:
            details = get_requests[fName]
            ln = len(details[0])

            if details[0] == path[0:ln] :
                rest_of_url = path[ln+1:]
                list_of_params = rest_of_url.split('/')
                list_of_params = [x for x in list_of_params if x != '']
                if len(list_of_params) == details[1] :
                    isExist = True
                    func  = globals()[fName](*list_of_params)
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(func)
                    # func
                    break

        if isExist == False:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'No Such Route Exists !!')

    def parse_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        response = BytesIO()
        response.write(b'This is POST request. ')
        response.write(b'Received: ')
        # response.write(body)
        # temp = json.loads(body)
        fields = parse_qs(body)
        keyPairs = {}

        for key, value in fields.iteritems():
            keyPairs[key] = value[0]

        return keyPairs

    def do_POST(self):
        keyPairs = self.parse_POST()

        path = self.path
        isExist = False

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
                    func  = globals()[fName](*list_of_params)
                    #self.send_response(200)
                    #self.end_headers()
                    self.wfile.write(func)
                    # func
                    break

        if isExist == False:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'No Such Route Exists !!')

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

class ManualRequest:
    def __init__(self, get_routes, post_routes, port_number):
        self.get_routes = get_routes
        self.post_routes = post_routes
        self.port_number = port_number

    def run(self):
        global get_requests
        global post_requests    
        get_requests = self.get_routes
        post_requests = self.post_routes
        httpd = ThreadedHTTPServer(('0.0.0.0', self.port_number), SimpleHTTPRequestHandler)
        httpd.serve_forever()

