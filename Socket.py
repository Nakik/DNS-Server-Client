import asyncio, socket

#Create Socket object.
#its like(exactly) the normal socket just Asyncio.
#Normal asyncio socket funcions to slow.
class Socket():
    def __init__(self, Socket: socket.socket):
        self.s = Socket
        self.s.settimeout(0.9) #I dont know why to put this. but its making the code works.-_-
        self.loop = asyncio.get_event_loop()
        self.ex = None
        
    async def Send(self, Data: bytes, addr: tuple=None):
        try:
            if isinstance(Data, str):
                if addr:
                    await self.loop.run_in_executor(self.ex, self.s.sendto, Data.encode(), addr)
                    return 1
                await self.loop.run_in_executor(self.ex, self.s.send, Data.encode())
                return 1
            if addr:
                await self.loop.run_in_executor(self.ex, self.s.sendto, Data, addr)
                return 1
            await self.loop.run_in_executor(self.ex, self.s.send, Data)
        except:
            return 0
    async def Bind(self, addr: type):
        try:
            await self.loop.run_in_executor(self.ex, self.s.bind, addr)
            return 1
        except:
            return 0
    async def Close(self):
        try:
            await self.loop.run_in_executor(self.ex, self.s.close)
            return 1
        except:
            return 0
    async def Connect(self, addr: type):
        try:
            await self.loop.run_in_executor(self.ex, self.s.connect, addr)
            return 1
        except:
            return 0
    async def Recv(self, timeout: int=None):
        if timeout != None:
            try:
              return await asyncio.wait_for(self.loop.run_in_executor(self.ex, self.s.recv, 1024), timeout=timeout)
            except:
                return 0
        else:
            try:
                return await self.loop.run_in_executor(self.ex, self.s.recv, 1024)
            except:
                return 0
    async def RecvFrom(self):
        try:
            return await self.loop.run_in_executor(self.ex, self.s.recvfrom, 1024)
        except:
            return 0, ""
    