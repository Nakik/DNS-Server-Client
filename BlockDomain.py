import asyncio
from NetworkClassHTTP import socket_farm #To download from links
import os #For the folder making.
import mmap
from DNSClient import DNSClient
from util import *

def convert_list_to_binary(filename):
    try:
        domain_set = set()
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                domain = line.strip()
                domain_set.add(domain.encode('utf-8'))
        return domain_set
    except Exception as e:
        print(f"Error reading file: {e}")
        return set()

Types_TO_block= {
    "Suspicious": [
"https://raw.githubusercontent.com/PolishFiltersTeam/KADhosts/master/KADhosts.txt",
"https://raw.githubusercontent.com/FadeMind/hosts.extras/master/add.Spam/hosts",
"https://v.firebog.net/hosts/static/w3kbl.txt",
"https://raw.githubusercontent.com/matomo-org/referrer-spam-blacklist/master/spammers.txt",
"https://someonewhocares.org/hosts/zero/hosts",
"https://raw.githubusercontent.com/VeleSila/yhosts/master/hosts",
"https://winhelp2002.mvps.org/hosts.txt",
"https://v.firebog.net/hosts/neohostsbasic.txt",
"https://raw.githubusercontent.com/RooneyMcNibNug/pihole-stuff/master/SNAFU.txt",
"https://paulgb.github.io/BarbBlock/blacklists/hosts-file.txt"
],
    "Advertising": [
"https://adaway.org/hosts.txt",
"https://v.firebog.net/hosts/AdguardDNS.txt",
"https://v.firebog.net/hosts/Admiral.txt",
"https://raw.githubusercontent.com/anudeepND/blacklist/master/adservers.txt",
"https://v.firebog.net/hosts/Easylist.txt",
"https://pgl.yoyo.org/adservers/serverlist.php?hostformat=hosts&showintro=0&mimetype=plaintext",
"https://raw.githubusercontent.com/FadeMind/hosts.extras/master/UncheckyAds/hosts",
"https://raw.githubusercontent.com/bigdargon/hostsVN/master/hosts",
"https://raw.githubusercontent.com/jdlingyu/ad-wars/master/hosts"
    ],
    "Malicious": [
"https://raw.githubusercontent.com/DandelionSprout/adfilt/master/Alternate%20versions%20Anti-Malware%20List/AntiMalwareHosts.txt",
"https://osint.digitalside.it/Threat-Intel/lists/latestdomains.txt",
"https://v.firebog.net/hosts/Prigent-Crypto.txt",
"https://raw.githubusercontent.com/FadeMind/hosts.extras/master/add.Risk/hosts",
"https://bitbucket.org/ethanr/dns-blacklists/raw/8575c9f96e5b4a1308f2f12394abd86d0927a4a0/bad_lists/Mandiant_APT1_Report_Appendix_D.txt",
"https://phishing.army/download/phishing_army_blocklist_extended.txt",
"https://gitlab.com/quidsup/notrack-blocklists/raw/master/notrack-malware.txt",
"https://v.firebog.net/hosts/RPiList-Malware.txt",
"https://v.firebog.net/hosts/RPiList-Phishing.txt",
"https://raw.githubusercontent.com/Spam404/lists/master/main-blacklist.txt",
"https://raw.githubusercontent.com/AssoEchap/stalkerware-indicators/master/generated/hosts",
"https://urlhaus.abuse.ch/downloads/hostfile/",
"https://malware-filter.gitlab.io/malware-filter/phishing-filter-hosts.txt",
"https://v.firebog.net/hosts/Prigent-Malware.txt"
    ],
}

class resolver():
    def __init__(self, client: DNSClient):
        self.client = client
    async def resolve(self, host, port, family) -> asyncio.Future:
        type = None
        if family == 0:
            type = dns_record_types["A"]
        an = await self.client.Send((await self.client.BuildQuery(type, host)).ToBytes())
        ans = Parse.DNSMessageToJSON(an)
        r = {
            "hostname": host,
            "host": ans.GetAnsers()[0].data,
            "port": 443,
            "family": 0,
            "proto":0,
            "flags": 0,
        }
        return [r]

def openfile(file):
    with open(file, 'r+b') as f:
        mmapped_file = mmap.mmap(f.fileno(), 0)
        data = mmapped_file.read()
        mmapped_file.close()
    return data
class BlockDomain():
    def __init__(self, types: list, client: DNSClient):
        self.client = client
        self.Lists = []
        folder = "BlockList"
        if not (os.path.exists(folder) and os.path.isdir(folder)):
            os.makedirs(folder)
        Types_TO_download = []
        for type in types:
            if type in Types_TO_block.keys():
                try:
                    open(f"BlockList/{type}.txt", "r").close()
                    self.Lists.append(f"BlockList/{type}.txt")
                except:
                    Types_TO_download.append(type)
        asyncio.create_task(self.DownloadLists(Types_TO_download))

    def CheckDomain(self, domain: str):
        #Binary_Domain = ''.join(format(ord(char), '08b') for char in domain)
        Binary_Domain = domain.encode("utf-8")
        for list in self.Lists:
            try:
                Z = openfile(list).split(b"\n")
            except FileNotFoundError:
                print("Please Restart Up to Re-download the files.")
                pass #You deleted the file. restart app to fix.
            if Binary_Domain in Z:
                return True
        return False
    async def DownloadLists(self, list: list):
        for type in list:
            await self.DownloadList(type)

    async def DownloadList(self, type: str):
        domains = ""
        print(f"Downloading {type} list.")
        Chunk = ""
        LinkNumber = 0
        MAX = len(Types_TO_block[type])
        Resolver = resolver(self.client)
        Httpclient = socket_farm(self.client)
        for link in Types_TO_block[type]:
            LinkNumber += 1
            x = 0
            response = await Httpclient.get(link)
            b = await response.text()
            lines = b.split("\n")
            total_lines = len(lines)  # Update the total number of lines dynamically
            for i in lines:
                if i == "\n" or i == "" or i[0] == "#":
                    continue
                if i[0] == "|":
                    i = i.replace("|", "")
                try:
                    Chunk += (i + "\n")
                    #Chunk += (i.split(" ")[1].split(" ")[0].split("\n")[0] + "\n")
                except IndexError:
                    continue
                x += 1
                if x % 1700 == 0:
                    print(f"{int((x / total_lines) * 100)}% Done. Link {LinkNumber}/{MAX} {type} list.")
                    domains += Chunk
                    Chunk = ""
        # Add remaining chunk to domains
        if Chunk:
            domains += Chunk
        print("Start Encoding.")
        open(f"BlockList/{type}.txt", "wb").write(domains.encode("utf-8"))
        self.Lists.append(f"BlockList/{type}.txt")
        return