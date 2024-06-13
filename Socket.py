import asyncio, socket

import contextvars, functools #To run the socket funcion in Asyncio.
#Create Socket object.
#its like(exactly) the normal socket just Asyncio.
#Normal asyncio socket funcions to slow.

class Socket():
    def __init__(self, Socket: socket.socket):
        self.s = Socket
        self.s.settimeout(0.4) #I dont know why to put this. but its making the code works.-_-
        self.loop = asyncio.get_event_loop()
        self.ex = None
    async def Run(self, fun, *args):
        ctx = contextvars.copy_context()
        return await self.loop.run_in_executor(None, functools.partial(ctx.run, fun, *args))

    async def Send(self, Data: bytes, addr: tuple=None):
        try:
            if isinstance(Data, str):
                Data = Data.encode()
            if addr:
                    await self.Run(self.s.sendto, Data, addr)
                    return 1
            await self.Run(self.s.send, Data)
        except:
            return 0
    async def Bind(self, addr: type):
        try:
            await self.Run(self.s.bind, addr)
            return 1
        except:
            return 0
    async def Close(self):
        try:
            await self.Run(self.s.close)
            return 1
        except:
            return 0
    async def Connect(self, addr: type):
        try:
            await self.Run(self.s.connect, addr)
            return 1
        except:
            return 0
    async def Recv(self, timeout: int=None):
        if timeout != None:
            fun = self.Run(self.s.recv, 1024, timeout)
        else:
            fun = self.Run(self.s.recv, 1024)
        try:
            return await fun
        except:
            return 0
    async def RecvFrom(self):
        try:
            return await self.Run(self.s.recvfrom, 1024)
        except:
            return 0, ""
    async def Accept(self):
        try:
            return await self.Run(self.s.accept)
        except:
            import traceback
            return 0, ""