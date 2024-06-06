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
import time
import psutil

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


#This is for Proxy.
try:
    if True:
        import ctypes
        ThisFodler = os.path.dirname(__file__)
        file = os.path.join(ThisFodler, "DNSProxyManagerWindow.py")
        if os.path.exists(file):
            if ctypes.windll.shell32.IsUserAnAdmin() == 0:
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, file, None, 2)
            else:
                import DNSProxyManagerWindow
except:
    print("Cant set DNS proxy.")

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

async def TestAndPrint(logger: Logger):
    try:
        cached_time, dotcom_time, uncached_time = await SpeedTest(My_IP, 53)
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
        }
        open(Settingfile, "w").write(json.dumps(Settings, indent=4))
    try:
        DDOS = False
        memory = False
        if Settings["Memory"] == 1:
            memory = True
        proxy = None
        if Settings["Proxy"] == 1:
            proxy = Proxy(FileToSave="Filters.txt")
        if Settings["Logs"] != 0:
            logger = Logger(file=Settings["Logs"])
        else:
            logger = None
        if Settings["DDOs"] != 0:
            DDOS = True
        if Settings["MemoryLogs"] != 0:
            asyncio.create_task(PrintInfo(Settings["MemoryLogs"], logger=logger))
        print("\033[93m" + "Starting Server on: ", f"0.0.0.0/{My_IP}" + "\033[0m") #My_IP from util.
        dns = DNSServer(logger=logger, Memory=memory, proxy=proxy, DDOS=DDOS)
        asyncio.create_task(dns.Main())
    except:
        print(traceback.format_exc())
    client = DNSClient(My_IP, 53)
    if True: #IDK!?
        inputes = Inputes(Client=client, Server=dns, Settings=Settings)
        asyncio.create_task(inputes.MainLoop())
    asyncio.create_task(client.Reader())
    #ask user if he want to run the speed test.
    if logger:
        if (await ainput("You want to run the speed test every 2 minutes? [y/n]: ")).lower() == "y":
            try:
                while True:
                    await TestAndPrint(logger)
                    await asyncio.sleep(120)
            except:
                print(traceback.format_exc())
    await asyncio.sleep(10000)

if __name__ == "__main__":
    asyncio.run(main())