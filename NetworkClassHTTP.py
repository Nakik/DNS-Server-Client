#This Code is part of my old HTTP library. I will use it here as its much easier to understand and faster and lighter than AioHttp.
#+For your own project you can use AioHttp. Its much better for big projects.
#safer and easier to use than This code.

import socket, ssl, asyncio
import datetime
from typing import Union
import json as _json
from urllib.parse import urlencode
import sys
from DNSClient import DNSClient

__version__ = "0.1"

def get_buffer(buffer: str):
    chunk_buffer = ""
    for i in buffer.split("\r\n"):
        try:
            int(i, 16)
        except:
            chunk_buffer += i
    return chunk_buffer

s = socket.socket

socket_count = 4

hosts = [
    ("discord.com", 4),
    ("fngw-mcp-gc-livefn.ol.epicgames.com", 6)
]

class Responses():
    def __init__(self, headers:dict, data:dict, url, status, message):
        self.headers = headers
        self.data = data
        self.url = url
        self.status = int(status)
        self.message = message
    async def text(self):
        return self.data
    
    async def json(self):
        return self.data
    def __str__(self):
        return f"Responses - {self.url} - {datetime.datetime.now()}"
    def __repr__(self):
        return f"Responses - {self.url} - {datetime.datetime.now()}"
    def __getitem__ (self, item):
        if item in self.headers.keys():
            return self.headers.get(item, None)
        
class Response():
    def __init__(self, response: str):
        self.response = response
        self.content_types = ["application/json", "text/plain", "text/html", "text/html; charset=UTF-8"]
        self.ct = None
        self.headers, self.body, self.first_line = self.get_headers(response)
        self.status, self.status_message = self.first_line[0].split(" ", 1)[1:][0].split(" ", 1)
    def get_headers(self, response: str):
        try:
            headers = response.split("\r\n\r\n")[0]
            headers = headers.split("\r\n")
            first_line = headers[:1]
            headers = headers[1:]
            headers_ = {}
            for header in headers:
                try:
                    headers_[header.split(": ")[0]] = header.split(": ")[1]
                except:
                    try:
                        headers_[header.split(":")[0]] = " "
                    except:
                        continue
                    continue
            headers = headers_
            if "204 No Content" in first_line[0]:
                return headers, "", first_line
            try:
                self.ct = headers['Content-Type']
                if not self.ct.startswith("application/json") and self.ct not in self.content_types:
                    return headers, "", first_line
            except:
                self.ct = "None"
            try:
                body = response.split("\r\n\r\n")[1]
            except:
                return headers , "", first_line
            if 'Content-Length' not in headers.keys() and "Transfer-Encoding" not in headers.keys():
                return headers, None, first_line
            if 'Content-Length' in headers.keys():
                if len(body) < int(headers['Content-Length']):
                    self.more_info = True
            return headers, body, first_line
        except:
            return {}, ""
        
    def __str__(self):
        return f'{self.status} - {self.status_message} - {self.ct} - {datetime.datetime.now()}'
    def __repr__(self):
        return f'{self.status} - {self.status_message} - {self.ct} - {datetime.datetime.now()}'

class socket_farm():
    def __init__(self, client: DNSClient):
        self.client = client
        self.context = ssl.create_default_context()
        self._lock = asyncio.Lock()
        self._pool = {}
        self.max_sockets = 145
        self.event = asyncio.Event()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        # Clean-up code, if any
        pass
    async def _get(self, host) -> s:
        #async with self._lock:
        if host not in self._pool.keys():
            return await self.create_socket(host)
        if len(self._pool[host]) < 1:
            return await self.create_socket(host)
        return self._pool[host].pop(0)

    async def socket_get(self, host):
        #if host == 'discord.com':
        #    try:
        #        raw_socket = await asyncio.get_running_loop().run_in_executor(None, socket.create_connection, (host, 443), 3)
        #    except:
        #        return await self.socket_get(host)
        #    ssl_socket = self.context.wrap_socket(raw_socket, server_hostname=host)
        #    return ssl_socket
        socket_ = await self._get(host)
        if socket_ == None:
            return await self.socket_get(host)
        socket_.setblocking(False)
        if await self.read(socket_, 4096) != b"": #clear socket if his not empty
            await self.clear_socket_buffer(socket_)
        socket_.setblocking(True)
        return socket_

    async def clear_socket_buffer(self,sock: socket.socket):
        try:
            while True:
                b = await self.read(sock,4096)
                if b == b"":
                    break
        except:
            pass
        finally:
            pass
        return  

#how to check if socket is still connected. WITHOUT sending message to it?

    async def release(self, host, socket, clear_buffer:bool=True):
        if host in self._pool.keys():
            self._pool[host].append(socket)
        else:
            self._pool[host] = [socket]

    async def _startup(self, host, socket_number):
        self._pool[host] = await self.create_sockets(host, socket_number)

    async def startup(self):
        funs_ = []
        for host, socket_number in hosts:
            funs_.append(self._startup(host, socket_number))
        await asyncio.gather(*funs_)
        
    async def create_socket(self, host, ip=None):
        if ip is None:
            try:
                raw_socket = await asyncio.get_running_loop().run_in_executor(None, socket.create_connection, (host, 443), 3)
                ssl_socket = await asyncio.get_running_loop().run_in_executor(None, self.context.wrap_socket, raw_socket, False, True, True, host)
                return ssl_socket
            except:
                return
        else:
            try:
                raw_socket = await asyncio.get_running_loop().run_in_executor(None, socket.create_connection, (ip, 443), 3)
                ssl_socket = await asyncio.get_running_loop().run_in_executor(None, self.context.wrap_socket, raw_socket, False, True, True, host)
                return ssl_socket
            except:
                return
    async def create_sockets(self, host: str, number = socket_count):
        ips = []
        for soc in await self.client.GlobalDNS(host):
            ips.append(soc)
        sockets_ = []
        for _ in range(number):
            sockets_.append(self.create_socket(host))
        sock = await asyncio.gather(*sockets_)
        return sock
    async def url_parse(self, data: Union[dict, str]):
        return urlencode(data)
    #create_body formtated json loads or data url parse
    async def post(self, url:str, headers:dict={}, data=None, json=None, response:bool=True, only_status:bool=False, timeout:int=3,params:dict={}, full_URI_:bool=False) -> Responses:
        return await self.request("post", url, headers, data, json, response, only_status, timeout,params, full_URI_)
    async def get(self, url:str, headers:dict={}, data=None, json=None, response:bool=True, only_status:bool=False, timeout:int=3,params:dict={}, full_URI_:bool=False) -> Responses:
        return await self.request("get", url, headers, data, json, response, only_status, timeout,params, full_URI_)
    async def put(self, url:str, headers:dict={}, data=None, json=None, response:bool=True, only_status:bool=False, timeout:int=3,params:dict={}, full_URI_:bool=False) -> Responses:
        return await self.request("put", url, headers, data, json, response, only_status, timeout,params, full_URI_)
    async def delete(self, url:str, headers:dict={}, data=None, json=None, response:bool=True, only_status:bool=False, timeout:int=3,params:dict={}, full_URI_:bool=False) -> Responses:
        return await self.request("delete", url, headers, data, json, response, only_status, timeout,params, full_URI_)
    async def patch(self, url:str, headers:dict={}, data=None, json=None, response:bool=True, only_status:bool=False, timeout:int=3,params:dict={}, full_URI_:bool=False) -> Responses:
        return await self.request("patch", url, headers, data, json, response, only_status, timeout,params, full_URI_)

    async def read(self,socket:s,bytes:int):
        loop = asyncio.get_running_loop()
        try:
            result = await loop.run_in_executor(None, socket.recv, bytes)
        except:
            return b""
        return result

    async def request(self, method:str, url:str,headers:dict={}, data=None, json=None, response:bool=True, only_status:bool=False, timeout:int=3,params={},full_URI_=False, new_socket=False) -> Responses:
        hosturi = url.removeprefix("https://")
        try:
            host, uri = hosturi.split("/", 1)
        except:
            host = hosturi
            uri = ""
        if json != None and data != None:
            raise ValueError("Cannot have both data and json parameters")
        if json != None:
            body = _json.dumps(json)
        elif data != None and headers.get("Content-Type", "") == "application/x-www-form-urlencoded":
            body = urlencode(data)
        elif data != None and headers.get("Content-Type", "") == "text/plain":
            if type(data) == str:
                body = data
            elif type(body) == bytes:
                pass
            else:
                raise ValueError("Body must be either str or bytes when content-type=text/plain")
        else:
            body = ""
        
        if type(params) == list:
            params_dict = {}
            for param in params:
                if param[0] not in params_dict.keys():
                    params_dict[param[0]] = param[1]
                else:
                    params_dict[param[0]] += f",{param[1]}"
            params = params_dict
        if params != {}:
            if '?' in uri:
                uri += '&' + '&'.join([f"{key}={value}" for key, value in params.items()])
            else:
                uri += '?' + '&'.join([f"{key}={value}" for key, value in params.items()])
        user_agent: str = 'Socket_farm/{0} Python/{1[0]}.{1[1]}'.format(__version__, sys.version_info)
        if full_URI_:
            request = (
                f"{method.upper()} {url} HTTP/1.1\r\n"
                f"Host: {host}\r\n"
                "Connection: keep-alive\r\n"
            )
        else:
            request = (
                f"{method.upper()} /{uri} HTTP/1.1\r\n"
                f"Host: {host}\r\n"
                "Connection: keep-alive\r\n"
            )
        if 'User-Agent' not in headers.keys():
            request += f"User-Agent: {user_agent}\r\n"
        if new_socket:
            socket = await self.create_socket(host)
        else:
            socket = await self.socket_get(host)
        if len(body) > 0 or method.lower() != "get":
            request += f"Content-Length: {len(body)}\r\n"
        if 'Content-Type' not in headers.keys():
            if data != None:
                headers['Content-Type'] = "application/x-www-form-urlencoded"
            elif json != None:
                headers['Content-Type'] = "application/json"
        for k,v in headers.items():
            request = request + f"{k}: {v}\r\n"
        #body_staff+
        request = request + f"\r\n{body}"
        socket.settimeout(3)
        try:
            await asyncio.get_event_loop().run_in_executor(None, socket.sendall, request.encode())
        except Exception as e:
            #await self.request(method, url, headers, data, json, response, only_status, timeout, params, new_socket=True)
            pass
        #if no need of response just return
        #if only status code is needed i will read just first 12 bytes split in first space as format of HTTPS is: HTTP/(version_without_spaces) (status_code) (status_message) #now as if its outdated https it can be 3 and 4 digit status codes so i will read 12 bytes.
        buffer = await self.read(socket,4096)
        if buffer == b'':
            asyncio.create_task(self.release(host, socket))
            return await self.request(method, url, headers, data, json, response, only_status, timeout, params, new_socket=True)
        if only_status == True:
            asyncio.create_task(self.release(host, socket))
            return Responses({}, None, url, int(buffer.split(b" ")[1].decode()), buffer.split(b" ")[2].decode())
        socket.settimeout(0.1)
        buffer_ = b""
        while True:
            b = await self.read(socket,4096)
            if b == b"":
                break
            if b"\r\n\r\n" in b:
                buffer_ += b
                break
            buffer_ += b
        buffer += buffer_
        socket.settimeout(3)
        if b'Transfer-Encoding' in buffer and buffer.split(b"Transfer-Encoding: ")[1].split(b"\r\n")[0].decode() == 'chunked' and (buffer.endswith(b"0\r\n\r\n") == False):
            while True:
                try:
                    b = await self.read(socket,4096)
                    if b.endswith(b"0\r\n\r\n"):
                        buffer += b
                        break
                    b = b
                    if not b:
                        break
                    if b == b"":
                        break
                    buffer += b
                except:
                    break
        else:
            if b'Content-Length: ' in buffer:
                content_length = int(buffer.split(b"Content-Length: ")[1].split(b"\r\n")[0])
                if content_length != len(buffer.split(b"\r\n\r\n")[1]):
                    while True:
                        try:
                            b = await self.read(socket,4096)
                            if not b:
                                break
                            if b == b"":
                                break
                            buffer += b
                            if content_length > len(buffer.split(b"\r\n\r\n")[1]):
                                break
                            if content_length == len(buffer.split(b"\r\n\r\n")[1]):
                                break
                        except:
                            break
        #socket.cookies = parse_cookies(buffer)
        #asyncio.create_task(self.set_cooke(buffer, socket))
        #send to Response class
        response = Response(buffer.decode())
        try:
            int(response.status)
        except:
            response.status = "200"
        if response.status == "204":
            asyncio.create_task(self.release(host, socket))
            return Responses(response.headers, None, url, int(response.status), response.status_message)
        #check for different content types and if its chunked encoding.
        if "Transfer-Encoding" in response.headers.keys() and "chunked" in response.headers['Transfer-Encoding']:
            response.body = get_buffer(response.body)
        if response.ct.startswith("application/json"):
            asyncio.create_task(self.release(host, socket))
            try:
                _json.loads(response.body)
            except:
                return Responses(response.headers, response.body, url, int(response.status), response.status_message)
            return Responses(response.headers, _json.loads((response.body)), url, int(response.status), response.status_message)
        #realse socket in case its not one of the above.
        asyncio.create_task(self.release(host, socket))
        return Responses(response.headers, response.body, url, int(response.status), response.status_message)