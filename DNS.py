Window_Title = "DNS Server + Client By Noki"
try:
    import pygetwindow as gw #This is for checking if the app is already running.
    windows = gw.getAllTitles()
    if Window_Title in windows:
        print("The app is already running.")
        if input("You want to continue? [y to continue): ").lower() != "y":
            exit()
except:
    pass

import os
os.system(f"title {Window_Title}") #Set title Why not?

#This libraries are default in python. so you dont need to install them.
import asyncio
import traceback
import sys
import json
try:
    import psutil
except:
    raise Exception("Please install psutil:\npip install psutil")

##############################################
#Importing the classes from the files.
#:`;:`;;;4z::;1
from DNSClient import DNSClient
from DNSServer import DNSServer
from DNSLogger import Logger
from Inputes import Inputes
from Proxy import Proxy
from util import *
from DNStest import SpeedTest
from Socket import Socket
from BlockDomain import BlockDomain
from DNSMemoryManager import DNSMemoryManager

#This is for Proxy.``
#try:
#    if True:
#        import ctypes
#        ThisFodler = os.path.dirname(__file__)
#        file = os.path.join(ThisFodler, "DNSProxyManagerWindow.py")
#        if os.path.exists(file):
#            if ctypes.windll.shell32.IsUserAnAdmin() == 0:
#                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, file, None, 2)
#            else:
#                import DNSProxyManagerWindow
#except:
#    print("Cant set DNS proxy.")

try:
    import colorama
    colorama.init()
except:
    pass #If you dont have colorama. its fine. its just for colors.

#"domains to skip. its mean it will send New DNS request to the server if it not in the memory dict"
#for endpoint that you dont care about speed and more about the data.
domains_skip = []

#the `Socket` Class. AIOsocket class. its like the normal socket but async.

def FirstPrint():
    print("\033[92m")
    print(r"""
    |  __ \| \ | |/ ____|                                | |           | \ | |     | |               
    | |  | |  \| | (___    ___  ___ _ ____   _____ _ __  | |__  _   _  |  \| | ___ | | ___   _  __ _ 
    | |  | | . ` |\___ \  / __|/ _ \ '__\ \ / / _ \ '__| | '_ \| | | | | . ` |/ _ \| |/ / | | |/ _` |
    | |__| | |\  |____) | \__ \  __/ |   \ V /  __/ |    | |_) | |_| | | |\  | (_) |   <| |_| | (_| |
    |_____/|_| \_|_____/  |___/\___|_|    \_/ \___|_|    |_.__/ \__, | |_| \_|\___/|_|\_\\__, |\__,_|
                                                                __/ |                    __/ |      
                                                               |___/                    |___/       
    """)
    print("\033[0m")
    print("\033[94m" + " "*30 + "DNS Server By Noki")
    print("\033[31m" + "Commands:")
    print("\033[35m" + "Client -> Send DNS queries.")
    print("\033[36m" + "Server -> Manage server; Proxy, auto anser, logs." + "\033[0m")
    print("\033[38m" + "Speed -> Check speed of a DNS server." + "\033[0m")

FirstPrint()

async def PrintInfo(Time:int=3, logger: Logger=None):
    if logger is None:
        return
    while True:
        try:
            #This is From psutil. its for checking the memory and CPU usage.
            #This code is modify version for AioDNS. so it will work with asyncio.
            #This code is not mine. I just modify it to work with asyncio.
            process = psutil.Process(os.getpid())
            mem_info = process.memory_info()
            Memory = BytesParse(mem_info.rss)
            #st1 = time.time()
            #pt1 = process.cpu_times()
            await asyncio.sleep(Time)
            #pt2 = process.cpu_times()
            #delta_proc = (pt2.user - pt1.user) + (pt2.system - pt1.system)
            #delta_time = time.time() - st1
            #overall_cpus_percent = ((delta_proc / delta_time) * 100)
            #single_cpu_percent = overall_cpus_percent * (psutil.cpu_count() or 1)
            #This CPU is not working so Skill issue. print just memory.
            msg = f"Memory: {Memory}"# - CPU: {single_cpu_percent:.2f}%"
            await logger.Print(msg)
        except:
            print(traceback.format_exc())

async def TestAndPrint(logger: Logger, addr: tuple):
    try:
        cached_time, dotcom_time, uncached_time = await SpeedTest(addr[0], addr[1])
        await logger.Print("Speed Test:")
        await logger.Print(f"Cached Time: {SetToString(cached_time)} - Same question in short time.")
        await logger.Print(f"Dotcom Time: {SetToString(dotcom_time)} - Dotcom domain Faster than random domain.")
        await logger.Print(f"Uncached Time: {SetToString(uncached_time)} - First time to ask the question.")
    except:
        print(traceback.format_exc())

async def main():
    Settingfile = "Settings.json"
    try:
        Settings = json.loads(open(Settingfile, "r").read())
    except:
        Settings = {
        "Memory": 1,
        "Proxy": 1,
        "Logs": "DNS.log",
        "MemoryLogs": 43,
        "DDOs": 1,
        "DNSQueriesBasedOnLocation": 1,
        "BlockMalicious": 1,
        "BlockSuspicious": 1,
        "BlockAdvertising": 1,
        "Country": "IL",
        }
        open(Settingfile, "w").write(json.dumps(Settings, indent=4))
    DNSServers: list[DNSServer] = []
    for ip in MyIps:
        print("\033[93m" + "Starting Server on: ", f"0.0.0.0/{ip}" + "\033[0m")
        port = Settings["Port"]
        DNSserver = DNSServer(ip=ip, port=port)
        asyncio.create_task(DNSserver.Main())
        DNSServers.append(DNSserver)
    client = DNSClient("23.167.232.7", port)
    await client.Initialize()
    PProxy = Proxy(FileToSave="Filters.txt")
    try:
        DDOS = False
        Memory = False
        Ip2Location = None
        if Settings["Memory"] == 1:
            Memory = True
            asyncio.create_task(DNSMemoryManager(memory).Loop())
        if Settings["Proxy"] == 1:
            ProxyEnables = True
        #    proxy = Proxy(FileToSave="Filters.txt")
        if Settings["Logs"] != 0:
            logger = Logger(file=Settings["Logs"])
        else:
            logger = None
        if Settings["DDOs"] != 0:
            DDOS = True
        if Settings["MemoryLogs"] != 0:
            asyncio.create_task(PrintInfo(Settings["MemoryLogs"], logger=logger))
        if Settings["DNSQueriesBasedOnLocation"] != 0:
            import IpDB
            try:
                Ip2Location = IpDB.IP2Location("IP2LOCATION-LITE-DB1.BIN")
            except:
                print("Cant load IP2Location DB.")
                #make sure to download it from the site.
                print("Download it from: https://lite.ip2location.com/")
        Block_list = []
        if Settings["BlockMalicious"] != 0:
            Block_list.append("Malicious")
        if Settings["BlockSuspicious"] != 0:
            Block_list.append("Suspicious")
        if Settings["BlockAdvertising"] != 0:
            Block_list.append("Advertising")
        Blocker = BlockDomain(Block_list, client=client)
    except:
        print(traceback.format_exc())
    for DNSserver in DNSServers:
        DNSserver.logger = logger
        DNSserver.Memory = Memory
        if ProxyEnables:
            DNSserver.proxy = PProxy
        DNSserver.DDOS = DDOS
        DNSserver.DBipLocation = Ip2Location
        DNSserver.BlockDomain = Blocker
        DNSserver.MyLocation = Settings["Country"]
        for Client in DNSserver.Socket.Sockets: #Install the servers i want Inside the Client. From the Server.
            client.AllClients.append(Client) #Add to the client list
    inputes = Inputes(proxy=PProxy, Client=client, DNSServers=DNSServers, Settings=Settings)
    await inputes.MainLoop()
    #while True:
    #    query = await client.BuildQuery(domain="1.1.1.1", type=dns_record_types["PTR"])
    #    ansers = await client.Send(query.ToBytes())
    #    an = Parse.DNSMessageToJSON(ansers)
    #    print(an)
    #    await asyncio.sleep(3)
    #if logger:
    #    if (await ainput("You want to run the speed test every 10 minutes? [y/n]: ")).lower() == "y":
    #        try:
    #            while True:
    #                await TestAndPrint(logger)
    #                await asyncio.sleep(600)
    #        except:
    #            print(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(main())