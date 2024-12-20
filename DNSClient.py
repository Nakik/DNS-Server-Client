import socket
from util import *
from Socket import Socket

class DNSClient():
    #Create the main connection. default is google DNS
    def __init__(self, IP: str=default_DNS_server, Port: int=PORT) -> None:
        self.ip = IP
        self.port = Port
        self.Socket = Socket(socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
        self.msg = {}
        self.Wait_list = {}
        self.Kill = True
        self.reader = None
        self.AllClients = [] 
        self.Key = 1
    async def Initialize(self):
        await self.Socket.Connect((self.ip, self.port))
        asyncio.create_task(self.Reader())
        return
    async def Reader(self):
        #start event with flag so you can end when you want. "Remember When you set flag to False. it will stop read until next Message."
        while self.Kill:
            try:
                data = await self.Socket.Recv()#read each data from the server. and put in the msg list.
                if data != 0:
                    _key = data[:2]
                    self.msg[_key] = data
                    self.Wait_list[_key].set() #Part of the event wait and key system.
            except:
                continue
        return
    async def Send(self, data: bytes) -> bytes:
        #Check and make sure Reader is not None. if it is. start the Reader.
        await self._send(data) #send the request to the main DNS server.
        r = await self.Wait_for(data[:2]) #wait for the response from the main DNS server.
        return r
    async def _send(self, data: bytes):
        await self.Socket.Send(data, (self.ip, self.port))

    async def Wait_for(self, _key):
        lock = Events() #Part of the event wait and key system.
        self.Wait_list[_key] = lock #Part of the event wait and key system.
        await lock.wait() #Part of the event wait and key system.
        response = self.msg[_key]
        del self.msg[_key]
        del self.Wait_list[_key] #Part of the event wait and key system.
        return response
    
    #Clean up funcion.-_-
    async def Close(self):
        await self.Socket.Close()
        del self.Socket
        self.Kill = False #To stop Reader Funcion.
        return
    async def BuildQuery(self, type: int=1, domain: str="example.com", class_: int=1):
        if type == 12:
            if len(domain.split('.')) == 4:
                domain = '.'.join(reversed(domain.split('.'))) + '.in-addr.arpa'
            else:
                reversed_nibbles = ''.join(domain[::-1].replace(':', ''))
                domain = '.'.join(reversed_nibbles) + '.ip6.arpa'
        key_ = format(self.Key, '04X')
        self.Key = (self.Key + 1) % 65536
        msg = DNSMessage(**{"id": key_, "!": False, "Q": [(domain, type, class_)], })
        msg.QR = 0
        return msg
    async def BuildResponse(self, msg: DNSMessage, anser: list):
        key_ = format(int(msg.id, 16), '04X')
        msg = DNSMessage(**{"id": key_, "!": True, "Q": msg.GetQuestions(), "A": anser})
        msg.QR = 1
        return msg
    
    async def GlobalDNS(self, domain: str, type: int=1, class_: int=1):
        msg = await self.BuildQuery(type, domain, class_)
        ansers = []
        funcs = []
        responses = []
        for Server in self.AllClients:
            funcs.append(Server.Send(msg.ToBytes()))
        responses = await asyncio.gather(*funcs)
        for query in responses:
            anser = Parse.DNSMessageToJSON(query)
            for a in anser.GetAnsers():
                if a.data not in ansers:
                    ansers.append(a.data)
        return ansers