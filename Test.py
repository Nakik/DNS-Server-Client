import asyncio
from aioconsole import ainput

def FirstPrint():
    print("\033[92m")
    print("""
    |  __ \| \ | |/ ____|                                | |           | \ | |     | |               
    | |  | |  \| | (___    ___  ___ _ ____   _____ _ __  | |__  _   _  |  \| | ___ | | ___   _  __ _ 
    | |  | | . ` |\___ \  / __|/ _ \ '__\ \ / / _ \ '__| | '_ \| | | | | . ` |/ _ \| |/ / | | |/ _` |
    | |__| | |\  |____) | \__ \  __/ |   \ V /  __/ |    | |_) | |_| | | |\  | (_) |   <| |_| | (_| |
    |_____/|_| \_|_____/  |___/\___|_|    \_/ \___|_|    |_.__/ \__, | |_| \_|\___/|_|\_\\__, |\__,_|
                                                                __/ |                    __/ |      
                                                               |___/                    |___/       
    """)
    print("\033[0m")
    print("\033[94m" + " "*30 + "DNS Server By Noki" + " "*30 + "\033[0m")
    print("\033[92m")
    print("\033[36m")
    print("\033[31m" + "Commands:")
    print("\033[35m" + "Client -> Send DNS queries.")
    print("\033[36m" + "Server -> Manage server; Proxy, auto anser, logs.")
    print("\033[0m")
FirstPrint()

import re

def Domain(dom):
    pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    if re.match(pattern, dom):
        return True
    else:
        return False
    
class Inputes():
    def __init__(self, Client = None, Server = None):
        self.Client = Client
        self.Server = Server
                               #Exit, DNSclient, DNsServer(Change settings...)
        self.Global_Commands = ["exit", "client", "server"]
        self._Shorts = {
            "e": "exit",
            "c": "client",
            "cli": "client",
            "s": "server",
            "ser": "server"
        }
        self.SubCommandsC = {
            "set": self.Set,
            "speed": self.Speed
        }
        self.SubCommandsS = {
            "proxy": self.Proxy,
            "memory": self.Memory,
            "logs": self.Logs
        }
    def logs(self, args):
        if args == "on":
            self.Server.Logs = True
        elif args == "off":
            self.Server.Logs = False
        else:
            print("\033[31m" + "Invalid argument." + "\033[0m")
    def Comm(self, command):
        if command == "exit":
            return None
        elif command == "client":
            print("Client commands:")
            print("exit -> Exit client.")
            print("domain(Domain) -> Send a DNS query to the server.")
            print("set type/server -> Set the server(DNS server) OR type(Question type).")
            print("Speed -> Check speed of a DNS server.")
            
        elif command == "server":
            print("Server commands:")
            print("exit -> Exit server.")
            print("Proxy -> Enable/Disable proxy.")
            print("Memory -> Enable/Disable memory cache.")
            print("Logs -> Enable/Disable logs.")
    async def ClientComm(self):
        print("\033[31m" + "Client is not connected.\n You want to create a new client? (y/n)" + "\033[0m")
        r = await ainput()
        if r == "y":
            self.Client = DNSClient()
        else:
            return False
        return
    async def ServerComm(self):
        print("\033[31m" + "Client is not connected.\n You want to create a new client? (y/n)" + "\033[0m")
        r = await ainput()
        if r == "y":
            self.Client = DNSServer()
        else:
            return False
        return
    
    async def MainLoop(self):
        while True:
            command = await ainput()
            command, args = command.lower().split(" ", 1)
            if command in self._Shorts.keys():
                command = self._Shorts[command]
            elif command in self.Global_Commands:
                self.Comm(command)
                continue
            elif command in self.SubCommandsC.keys():
                if not self.Client:
                    if (await self.ClientComm()) == False:
                        continue
                self.SubCommandsC[command](args)
                continue
            elif command in self.SubCommandsS.keys():
                if not self.Server:
                    if (await self.ServerComm()) == False:
                        continue
                self.SubCommandsS[command](args)
                continue
            if Domain(command):
                if not self.Client:
                    if (await self.ClientComm()) == False:
                        continue
                r = await self.Client.Query(command)
                print(self.AnserTOStr(r))
                continue
            else:
                print("\033[31m" + "Command not found." + "\033[0m")
i = Inputes()

asyncio.run(i.MainLoop())
