import asyncio
import aiohttp #To download from links
import os #For the folder making.

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

class BlockDomain():
    def __init__(self, types: list):
        self.Lists = []
        folder = "BlockList"
        if not (os.path.exists(folder) and os.path.isdir(folder)):
            os.makedirs(folder)
        for type in types:
            if type in Types_TO_block:
                try:
                    self.Lists.append(open(f"BlockList/{type}.txt", "rb").read().split(b"\n"))
                except:
                    asyncio.create_task(self.DownloadList(type))

    def CheckDomain(self, domain: str):
        domain = domain.encode('utf-8')
        for list in self.Lists:
            if domain in list:
                return True
        return False
    async def DownloadList(self, type: str):
        domains = ""
        async with aiohttp.ClientSession() as session:
            for link in Types_TO_block[type]:
                async with session.get(link) as response:
                    b = await response.text()
                    for i in b.split("\n"):
                        if i.startswith("#"):
                            continue
                        if i == "\n" or i == "":
                            continue
                        try:
                            domain = (i.split(" ")[1].split(" ")[0].split("\n")[0] + "\n").replace("www.", "")
                            domains += domain
                        except:
                            continue
        D = domains.encode()
        open(f"BlockList/{type}.txt", "wb").write(D)
        self.Lists.append(D.split(b"\n"))
        return