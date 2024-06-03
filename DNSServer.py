import asyncio
import socket
import struct
import random
import time
from util import *
from util import memory
from DNSClient import DNSClient
from DNSLogger import Logger
from Socket import Socket
from Proxy import Proxy
import traceback

#This class is basically To know always what is the best DNS server based on TTA(Time To Anser).
#every 50 requests it will return Random socket from the list. and every 10 random. it will be back to just Best socket.
class DNSServers():
    def __init__(self, List=DNSServer_List):
        SocketList = []
        for Ip, Port in List:
            client = DNSClient(Ip, Port)
            asyncio.create_task(client.Reader()) #start the reader. to read the response from the main DNS server.
            SocketList.append(client)
        self.Sockets = tuple(SocketList)
        self.LastBestTime = 12
        self.XS = 20
        self.ZX = 0
        self.NS = 0
    def Get(self) -> DNSClient:
        if self.XS == 20:
            if self.ZX == 10:
                self.XS = 0
                self.ZX = 0
                return self.Sockets[0]
            self.ZX += 1
            if self.NS > len(self.Sockets):
                self.NS = 0
            return self.Sockets[self.NS]
        self.XS += 1 #Add 1 to counter.
        return self.Sockets[0]
    
    def Update(self,socket,time):
        if time < self.LastBestTime:
            New = []
            New.append(socket)
            for S in self.Sockets:
                if S is not socket:
                    New.append(S)
            self.Sockets = tuple(New)
    async def Close(self):
        for s in self.Sockets:
            await s.Close()
        return
    
class DNSServer():
    def __init__(self, ip: str="0.0.0.0", port: int=53, logger: Logger=None, Memory: bool=True, proxy: Proxy=None):
        self.logger = logger
        self.ip = ip
        self.port = port
        self.Memory = Memory
        self.proxy = proxy
    async def Main(self):
        self.loop = asyncio.get_event_loop()
        self.Socket = DNSServers() #This class is basically To know always what is the best DNS server based on TTA(Time To Anser).
        #asyncio.create_task(self.Task()) #Start task. this task set the Main_DNS as the Best DNS server. based on the anser time. #But its better to use DNSServers class. much better.
        self.server_socket = Socket(socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
        await self.server_socket.Bind((self.ip, self.port))
        while True:
            try:
                data, addr = await self.server_socket.RecvFrom()
            except:
                continue
            try:
                asyncio.create_task(asyncio.wait_for(self.HandleQuery(data, addr), 9))#9 seconds its more than enough for DNS.
                #Creating task for each new query is better. it just for the Send and Wait for response part. But it can be really effective.
                #the wait_for, is so it will not open task without close. some times it can miss and just get stuck on the Wait for Response funcion(wait_for()).
            except:
                pass
    def ClearMemory(self):
        memory.memory = {}
    
    async def Close(self):
        await self.server_socket.Close()
        await self.Socket.Close()

        return
    async def HandleQuery(self, data: bytes, addr: tuple):
        try:
            if data == 0 or not 0 == (data[:12][2] >> 7) & 1:
                return
            requests = await Parse.DNSMessageToJSON(data)#DNSMessage
            ADDRString, Process = GetAddrString(addr)
            #ADDRString = For logger.
            #Process = This to using To proxy all process DNS to same IP.
            if self.logger:
                await self.logger.Log(requests, ADDRString)
                Time = time.time()
            if self.proxy:
                r = self.proxy.CheckProxy(requests)
                if r:
                    if self.logger:
                                ADDRString += " - Auto Proxy Anser"
                                await self.logger.Log(r, ADDRString, Time=time.time()-Time)
                    await self.server_socket.Send(r.ToBytes(), addr)#send the response to the client.
                    return
            anser = None
            if self.Memory and requests.NotFine is False:
                r, AA = memory.Check(requests)
                if r:
                    anser = BuildAnser(requests, r, AA) #Build ansers. based on requests, with ansers from Memory. And convert to Bytes(DNS format.)
                    try:
                        Key_vault.remove(format(struct.unpack('!H', data[:2])[0], '04X')) #remove key from Key vault.
                    except:
                        pass
                    if self.logger:
                        ADDRString += " - Memory Anser"
                        await self.logger.Log(anser, ADDRString, Time=time.time()-Time)
                    await self.server_socket.Send(anser.ToBytes(), addr)#send the response to the client.
                    return
            try:
                Key_vault.remove(format(struct.unpack('!H', data[:2])[0], '04X')) #remove key from Key vault.
            except:
                pass
            socket = self.Socket.Get()
            TTA = time.time() #Start time counter
            Anser = await socket.Send(data) #send the request to the main DNS server. And wait for response. _><_
            #if anser != None:
            #    print(Anser, '\n', anser.ToBytes())
            self.Socket.Update(socket, time.time()-TTA) #End time counter. Update the socket time
            if not 1 == (Anser[:12][2] >> 7) & 1:
                return
            Anser_ = await Parse.DNSMessageToJSON(Anser)#DNSMessage
            if self.Memory and Anser_.NotFine is False:
                memory.Save(Anser_)
            try:
                await asyncio.wait_for(self.server_socket.Send(Anser, addr), 2)
            except:
                pass
            if self.logger:
                await self.logger.Log(Anser_, ADDRString, Time=time.time()-Time, Server=socket.Socket.s.getpeername()[0])
            return
        except GeneratorExit:
            return #Cant do anything. its sucks.
        except asyncio.exceptions.CancelledError:
            return
        except:
            print(traceback.format_exc())
            return
        
    #Funcion to get Best server IP. 
    async def GetBestDNSServer(self, list) -> str:
        tasks = []
        #generate avrage Query(type a class a).
        query = DNSMessage(**{"!": False, "id": "1251", "qr": 0, "Q": [("example.com", 1, 1)], }).ToBytes()
        async def SendDNS(IP: str):
            sock = Socket(socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
            start_time = time.time()
            #Send 3 times same Query.
            for _ in range(3):
                await sock.Send(query, (IP, 53))
                try:
                    await asyncio.wait_for(sock.RecvFrom())
                except:
                    return None
            return time.time() - start_time
        #Get all servers from List
        for server_ip in list:
            tasks.append(SendDNS(server_ip))
        response_times = await asyncio.gather(*tasks) #Call all the SendDNS funcions.
        results = {}
        for server_ip, response_time in zip(list, response_times): #the IP list and Response times list.
            if response_time is not None:
                results[server_ip] = response_time
        if results:
            fastest_server = min(results, key=results.get)
            return fastest_server, results[fastest_server]
        #Thank(to!GPT@by$openAI%for^this*code -_- lol.
        else:
            return None, None
