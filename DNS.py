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

#This libraries are default in python. so you dont need to install them.
import asyncio
import traceback
import sys
import json
import os
import time

##############################################
from DNSClient import DNSClient
from DNSServer import DNSServer
from DNSLogger import Logger
from Inputes import Inputes
from Proxy import Proxy
from util import *
#This is for Proxy.

os.system(f"title {Window_Title}")

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
    print("\033[93m" + "Starting app on: ", My_IP + "\033[0m") #My_IP from util.
     
FirstPrint()

async def main():
    Settingfile = "Settings.json"
    try:
        Settings = json.loads(open(Settingfile, "r").read())
    except:
        Settings = {
            "Memory": 1,
            "Proxy": 1,
            "Logs": "DNS.log"
        }
        open(Settingfile, "w").write(json.dumps(Settings, indent=4))
    try:
        memory = False
        if Settings["Memory"] == 1:
            memory = True
        proxy = None
        if Settings["Proxy"] == 1:
            proxy = Proxy(FileToSave="Filters.txt")
        if Settings["Logs"] != 0:
            logger = Logger(file=Settings["Logs"])
        dns = DNSServer(logger=logger, Memory=memory, proxy=proxy)
        asyncio.create_task(dns.Main())
    except:
        print(traceback.format_exc())
    client = DNSClient(My_IP, 53)
    if True: #IDK!?
        inputes = Inputes(Client=client, Server=dns, Settings=Settings)
        asyncio.create_task(inputes.MainLoop())
    asyncio.create_task(client.Reader())
    while True:
        query = await client.BuildQuery(type=dns_record_types["A"], domain="example.com")
        TTA = time.time()
        r = await client.Send(query.ToBytes())
        anser = await Parse.DNSMessageToJSON(r)
        #print(f"Time: {SetToString(time.time() - TTA)}\nAnsers:")
        #for ans in anser.GetAnsers():
        #    print(ans)
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())