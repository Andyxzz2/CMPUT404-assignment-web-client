#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
from urllib.parse import urlparse, urlencode

def help():
    print("httpclient.py [GET/POST] [URL]\n")


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body


class HTTPClient(object):
    # def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        header = self.get_headers(data).split()
        code = header[1]
        return int(code)

    def get_headers(self, data):
        header = data.split('\r\n\r\n')[0]
        
        return header

    def get_body(self, data):#return None  if body doesn't exist
        try:
            return data.split('\r\n\r\n')[1]
        except:
            return None
    #send all data
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        #keep track the ;ength of the data, each packge is 1024 bits long
        while True:
            next_packge = sock.recv(1024)
            if (next_packge):
                buffer.extend(next_packge)
            else:
                break
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        #parse url to get port, host, path
        u = urlparse(url)
        port = u.port
        host = u.hostname
        path = u.path
        self.connect(host, port)

        #
        if path == '':
            path = '/'
        if args != None:
            path = path + "?" + args    #handling query
        #send the get request
        request = f'GET {path} HTTP/1.1\r\nHost: {host}\r\nAccept: */*\r\nConnection: close\r\n\r\n'
        self.sendall(request)
        data = self.recvall(self.socket)
        code = self.get_code(data)
        body = self.get_body(data)
        print(body)
        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        u = urlparse(url)
        port = u.port
        host = u.hostname
        path = u.path

        self.connect(host, port)
        if path == '':
            path = '/'
        if args == None:
            args = ''
        else:
            args = urlencode(args)
        #send post request
        length = len(args)
        request = '''POST {path} HTTP/1.1\r\nHost: {host}\r\nContent-Type: application/x-www-form-urlencoded\r\nAccept:*/*\r\nContent-Length: {length}\r\nConnection: close\r\n\r\n'''+args
        self.sendall(request)
        data = self.recvall(self.socket)
        code = self.get_code(data)
        body = self.get_body(data)
        print(body)
        self.close()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command(sys.argv[2], sys.argv[1]))
    else:
        print(client.command(sys.argv[1]))
