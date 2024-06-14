#This file is like a manager for the Server Memory class.
#if cached is On(save ansers in memory) This file(Class) will check if the Anser is still valid.
#Its using something that called rDNS. Its reverse DNS. its convert Ip to domain.
from util import Memory
import asyncio
import datetime

class DNSMemoryManager():
    def __init__(self, memory:Memory) -> None:
        self.memory = memory
    async def Loop(self):
        while True:
            await asyncio.sleep(30) #Check every 30 seconds.
            for key, value in self.memory.memory.copy().items():
                if (datetime.datetime.now() - datetime.datetime.strptime(value["last_update"], "%Y-%m-%d %H:%M:%S")).seconds > value["TTL"]:
                    self.memory.memory.pop(key)