import asyncio, socket

import contextvars, functools #To run the socket funcion in Asyncio.
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
            ctx = contextvars.copy_context()
            if isinstance(Data, str):
                Data = Data.encode()
            if addr:
                    func_call = functools.partial(ctx.run, self.s.sendto, Data, addr)
                    await self.loop.run_in_executor(self.ex, func_call)
                    return 1
            func_call = functools.partial(ctx.run, self.s.send, Data)
            await self.loop.run_in_executor(self.ex, func_call)
        except:
            return 0
    async def Bind(self, addr: type):
        try:
            ctx = contextvars.copy_context()
            func_call = functools.partial(ctx.run, self.s.bind, addr)
            await self.loop.run_in_executor(self.ex, func_call)
            return 1
        except:
            return 0
    async def Close(self):
        try:
            ctx = contextvars.copy_context()
            func_call = functools.partial(ctx.run, self.s.close)
            await self.loop.run_in_executor(self.ex, func_call)
            return 1
        except:
            return 0
    async def Connect(self, addr: type):
        try:
            ctx = contextvars.copy_context()
            func_call = functools.partial(ctx.run, self.s.connect, addr)
            await self.loop.run_in_executor(self.ex, func_call)
            return 1
        except:
            return 0
    async def Recv(self, timeout: int=None):
        ctx = contextvars.copy_context()
        if timeout != None:
            func_call = functools.partial(ctx.run, self.s.recv, 1024)
            fun = asyncio.wait_for(self.loop.run_in_executor(self.ex, func_call), timeout=timeout)
        else:
            func_call = functools.partial(ctx.run, self.s.recv, 1024)
            fun = self.loop.run_in_executor(self.ex, func_call)
        try:
            return await fun
        except:
            return 0
    async def RecvFrom(self):
        try:
            ctx = contextvars.copy_context()
            func_call = functools.partial(ctx.run, self.s.recvfrom, 1024)
            return await self.loop.run_in_executor(self.ex, func_call)
        except:
            return 0, ""
    