import asyncio
import json
import os
from DNSClient import DNSClient
from DNSServer import DNSServer
from util import *
from DNSLogger import Logger
from Proxy import Proxy
from DNStest import SpeedTest
import traceback

class Inputes():
    def __init__(self, proxy: Proxy, Client: DNSClient = None, DNSServers: list[DNSServer] = None, Settings: dict=None):
        self.Client = Client
        self.DNSServers = DNSServers
        self.type = ["A", "AAAA"]
        self.proxy = proxy
        if not Settings:
            self.Settingfile = "Settings.json"
            self.Settings = json.loads(open(self.Settingfile, "r").read())

        if self.Client:
            self.DNSServer = Client
        else:
            client = DNSClient("8.8.8.8", 53)
            self.Reader = asyncio.create_task(client.Reader()) #start the reader.
                               #Exit, DNSclient, DNsServer(Change settings...)
        self.Global_Commands = ["exit", "client", "server", "speed"]
        self._Shorts = {
            "e": "exit",
            "c": "client",
            "cli": "client",
            "s": "server",
            "ser": "server"
        }
        self.SubCommandsC = {
            "set": self.Set,
        }
        self.SubCommandsS = {
            "proxy": self.Proxy,
            "memory": self.Memory,
            "logs": self.Logs
        }
        self.ARGS = {
            "set": ["type", "server"],
            "proxy": ["on", "off", "manager"],
            "memory": ["on", "off"],
            "logs": ["on", "off"],
        }
    
    def UpdateSettings(self, key, value):
        self.Settings[key] = value
        with open(self.Settingfile, "w") as f:
            f.write(json.dumps(self.Settings))

    async def Logs(self, args):
        #if Path is None. ask user for path to save the logs.
        #if self.logger is None:
        #    #ask user for path to save the logs.
        #    print("Enter the path to save the logs (Leave empty to save default):")
        #    path = await ainput()
        #    self.UpdateSettings("Logs", path)
        #    for server in self.DNSServers:
        #        server.logger = Logger(path)
        if args == "on":
            for server in self.DNSServers:
                server.logger._X = True
            print("Logs are enabled.")
        elif args == "off":
            self.UpdateSettings("Logs", 0)
            for server in self.DNSServers:
                server.logger._X = False
            print("Logs are disabled.")
        else:
            print("\033[31m" + "Invalid argument. on/off" + "\033[0m")
    async def Memory(self, args):
        if args == "on":
            self.UpdateSettings("Memory", 1)
            for server in self.DNSServers:
                server.Memory = True
            print("Memory is enabled.")
        elif args == "off":
            self.UpdateSettings("Memory", 0)
            for server in self.DNSServers:
                server.Memory = False
                server.ClearMemory()
            print("Memory is disabled.")
        else:
            print("\033[31m" + "Invalid argument. on/off" + "\033[0m")
    async def Proxy(self, args):
        if args == "manager":
            print("Welcome to the Proxy options manager.")
            print("Here you can add, remove, and see the proxies rules/Filters.")
            print("Commands:")
            while True:
                print("\033[33m" + "Add -> Add a new Proxy Rule/Filters." + "\033[0m")
                print("\033[32m" + "Remove (number from List) -> Remove a Proxy Rule/Filters." + "\033[0m")
                print("\033[34m" + "List -> List all the Proxy Rules/Filters." + "\033[0m")
                print("Exit -> Exit the Proxy options manager.")
                command = await ainput()
                if command == "exit":
                    print("Exiting the Proxy options manager.")
                    break
                if command == "add":
                    print("Enter the domain/value: (Type stop to stop)")
                    domain = await ainput()
                    if value == "stop":
                        continue
                    print("Enter the type(IP->1/A): (Type stop to stop)")
                    type = await ainput()
                    if value == "stop":
                        continue
                    print("Enter the Target(Ip/Domain depend on value.): (Type stop to stop)")
                    value = await ainput()
                    if value == "stop":
                        continue
                    open("Filters.txt", "a").write(f'\nQ.domain == "{domain.strip()}" & Q.type == {type.strip()} -> {value.strip()}')
                    print("Rule/Filter Added.")
                    print("Rules/Filters:")
                    X = 1
                    for proxy in self.proxy.options:
                        option = ""
                        for o in proxy[0]:
                            option += o + " & "
                        option = option[:-3]
                        print(f"{X}. {option} -> {proxy[1]}")
                        X += 1
                elif command.startswith("remove"):
                    try:
                        number = int(command.split(" ")[1].strip())
                    except:
                        print("\033[31m" + "Invalid number. Run the command: `remove {rule number}`" + "\033[0m")
                        continue
                    if number > len(self.proxy.options):
                        print("\033[31m" + "Invalid number." + "\033[0m")
                        continue
                    self.proxy.options.pop(number-1)
                    await self.proxy.UpdateFile()
                    print("Rule/Filter removed.")
                    print("Rules/Filters:")
                    X = 1
                    for proxy in self.proxy.options:
                        option = ""
                        for o in proxy[0]:
                            option += o + " & "
                        option = option[:-3]
                        print(f"{X}. {option} -> {proxy[1]}")
                        X += 1
                elif command == "list":
                    print("Proxies:")
                    X = 1
                    for proxy in self.proxy.options:
                        option = ""
                        for o in proxy[0]:
                            option += o + " & "
                        option = option[:-3]
                        print(f"{X}. {option} -> {proxy[1]}")
                        X += 1
                else:
                    print("\033[31m" + "Command not found." + "\033[0m")
        elif args == "on":
            for server in self.DNSServers:
                server.proxy = self.proxy
            self.UpdateSettings("Proxy", 1)
            print("Proxy is enabled.")
        elif args == "off":
            for server in self.DNSServers:
                server.proxy = None
            self.UpdateSettings("Proxy", 0)
            print("Proxy is disabled.")
        else:
            print("\033[31m" + "Invalid argument. on/off" + "\033[0m")
    def Speed(self, args):
        #Not yet implemented.
        pass
    async def Set(self, args):
        if args.split(" ")[0] == "server":
            Server_ip = args.split(" ")[1]
            Port = 53
            if ":" in Server_ip:
                Server_ip, Port = Server_ip.split(":")
                Port = int(Port)
            try:
                #Create new DNSClient object.
                self.Client = DNSClient(Server_ip, Port) #Its probably port 53.
                Reader = asyncio.create_task(self.Client.Reader()) #start the reader.
                #But kill last reader.
                self.Reader.cancel()
                self.Reader = Reader
            except:
                print("Cant connect to the server.")
        elif args.split(" ")[0] == "type":
            Type = args.split(" ")[1].upper()
            try:
                Type = int(Type)
            except:
                pass
            if KEYTOVALUE(dns_record_types, Type):
                self.type = KEYTOVALUE(dns_record_types, Type)
                print("Type set to:", self.type)
            elif Type in dns_record_types.keys():
                self.type = Type
                print("Type set to:", self.type)
            else:
                print("\033[31m" + "Invalid type." + "\033[0m")
        else:
            print("\033[31m" + "Invalid argument." + "\033[0m")
    def Comm(self, command):
        if command == "exit":
            return None
        elif command == "client":
            print("Client commands:")
            print("domain(Domain) -> Send a DNS query to the server.")
            print("set type/server -> Set the server(DNS server) OR type(Question type).")
            print("Speed -> Check speed of a DNS server.")
            
        elif command == "server":
            print("Server commands:")
            print("Proxy -> Enable/Disable proxy.")
            print("Memory -> Enable/Disable memory cache.")
            print("Logs -> Enable/Disable logs.")
        elif command == "speed":
            print("Speed Test commands:")
            print("Speedtest <ip>:port=53 -> Start the Speedtest for the server.")
            print("Speedtest Without argument -> Start the Speedtest for the current server.")

    async def ClientComm(self):
        print("\033[31m" + "Client is not connected.\n You want to create a new client? (y/n)" + "\033[0m")
        r = await ainput()
        if r == "y":
            self.Client = DNSClient()
        else:
            return False
        return
    async def ServerComm(self):
        print("\033[31m" + "Server is not connected.\n You want to create a new Server? (y/n)" + "\033[0m")
        r = await ainput()
        if r == "y":
            self.Client = DNSServer()
        else:
            return False
        return
    
    async def MainLoop(self):
        while True:
            command = await ainput()
            try:
                command, args = command.lower().split(" ", 1)
            except:
                command = command.lower()
                args = None
            if command == "exit":
                #Exit the app.
                await self.Client.Close()
                for server in self.DNSServers:
                    await server.Close()
                os._exit(1)
            if command in self._Shorts.keys():
                command = self._Shorts[command]
            elif command in self.Global_Commands:
                self.Comm(command)
                continue
            if command == "speedtest":
                ip = None
                port = 53
                if args:
                    if ":" in args:
                        ip, port = args.split(":")
                        port = int(port)
                    else:
                        ip = args
                    print(f"Starting Speed Test. On: {ip}:{port}")
                    cached_time, dotcom_time, uncached_time = await SpeedTest(ip, port)
                    print("Speed Test Results:")
                    print("\033[31m" + f"Cached Time: {SetToString(cached_time)} - Same question in short time.")
                    print("\033[32m" + f"Dotcom Time: {SetToString(dotcom_time)} - Dotcom domain Faster than random domain.")
                    print("\033[33m" + f"Uncached Time: {SetToString(uncached_time)} - First time to ask the question." + "\033[0m")
                else:
                    if not self.Server:
                        if (await self.ServerComm()) == False:
                            continue
                    print(f"Starting Speed Test. On: Self Server.")
                    cached_time, dotcom_time, uncached_time = await SpeedTest(MyIps[0], port)
                    print("Speed Test Results:")
                    print("\033[31m" + f"Cached Time: {SetToString(cached_time)} - Same question in short time.")
                    print("\033[32m" + f"Dotcom Time: {SetToString(dotcom_time)} - Dotcom domain Faster than random domain.")
                    print("\033[33m" + f"Uncached Time: {SetToString(uncached_time)} - First time to ask the question." + "\033[0m")
            elif Domain(command):
                if not self.Client:
                    if (await self.ClientComm()) == False:
                        continue
                r = await self.Query(command)
                self.PrintAnser(r)
                continue
            elif command in self.SubCommandsC.keys():
                if not args:
                    #Need to put args on commands
                    print("\033[31m" + "Command need argument." + "\033[0m")
                    Args = ", ".join(self.ARGS[command])
                    print("Args:", Args)
                    continue
                if not self.Client:
                    if (await self.ClientComm()) == False:
                        continue
                await self.SubCommandsC[command](args)
                continue
            elif command in self.SubCommandsS.keys():
                if not args:
                    #Need to put args on commands
                    print("\033[33m" + "Command need argument." + "\033[0m")
                    Args = ", ".join(self.ARGS[command])
                    print("Args:", Args)
                    continue
                if self.DNSServers == []:
                    if (await self.ServerComm()) == False:
                        continue
                await self.SubCommandsS[command](args)
                continue
            else:
                print("\033[31m" + "Command not found." + "\033[0m")

    async def Query(self, domain):
        ansers = []
        if isinstance(self.type, list):
            for t in self.type:
                try:
                    if isinstance(t, str):
                        t = dns_record_types[t]
                except:
                    continue
                query = await self.Client.BuildQuery(type=t, domain=domain)
                r = await self.Client.Send(query.ToBytes())
                anser = Parse.DNSMessageToJSON(r)
                if anser.GetAnsers():
                    ansers.append(anser)
        else:
            query = await self.Client.BuildQuery(type=self.type, domain=domain)
            r = await self.Client.Send(query.ToBytes())
            anser = Parse.DNSMessageToJSON(r)
            if anser.GetAnsers():
                ansers.append(anser)
        return ansers
    def PrintAnser(self, anser):
        for ans in anser:
            if isinstance(ans, DNSMessage):
                for an in ans.GetAnsers():
                    an = f"Anser For : {an.domain} - Type: {an.type} - Class: {an.Class} - TTL: {an.ttl} = {an.data}"
                    print(an)
        return