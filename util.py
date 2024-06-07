import socket #To Parse IP4/6 address.
import random #To create Random Keys.
from collections import deque
import asyncio
import re
from typing import List
import os
try:
    from aioconsole import ainput
except:
    raise Exception("Please install aioconsole. pip install aioconsole")
import datetime
import psutil #For logger And Proxy. to get process name.
import sys

default_DNS_server = "8.8.8.8"
PORT = 53
OFFLINE = False

def get_local_ip():
    if OFFLINE:
        return "127.0.0.1"
    try:
        s = socket.create_connection(("8.8.8.8", 53), )
        local_ip = s.getsockname()[0]
        return local_ip
    except Exception as e:
        raise Exception("No Network Connection.")

#This app Print funcion. its 100% useless. but Faster if you print all the things.
Console = sys.stdout
def Print(*k):
    Text = ""
    for Item in k:
        Text += str(Item)
        Text += " "
    Console.write(Text + "\n")

print = Print

My_IP = get_local_ip()
DNSServer_List = [
("1.0.0.1",53),            # Cloudflare DNS
("208.67.220.220",53),     # OpenDNS (Cisco)
("208.67.222.123",53),     # OpenDNS FamilyShield
("208.67.220.123",53),     # OpenDNS FamilyShield
('8.8.8.8', 53),           # Google Public DNS (Global)
('8.8.4.4', 53),           # Google Public DNS (Global)
('1.1.1.1', 53),           # Cloudflare DNS (Global)
('1.0.0.1', 53),           # Cloudflare DNS (Global)
('208.67.222.222', 53),    # OpenDNS (Global)
('208.67.220.220', 53),    # OpenDNS (Global)
('9.9.9.9', 53),           # Quad9 (Global)
('149.112.112.112', 53),   # Quad9 (Global)
('156.154.70.1', 53),      # Neustar UltraDNS (US, Global)
('156.154.71.1', 53),      # Neustar UltraDNS (US, Global)
('77.88.8.8', 53),         # Yandex.DNS (Russia, Global)
('77.88.8.1', 53),         # Yandex.DNS (Russia, Global)
('185.228.168.9', 53),     # CleanBrowsing DNS (Europe, Global)
('185.228.169.9', 53),     # CleanBrowsing DNS (Europe, Global)
] #list provided by Chat-GPT!.

DNSlocations = {
    "AU": ("1.0.0.1", 53),           # Cloudflare DNS
    "US": ("208.67.220.220", 53),    # OpenDNS (Cisco)
    "RU": ('77.88.8.8', 53),        # Yandex.DNS (Russia, Global)
    "GB": ('185.228.169.9', 53),    # CleanBrowsing DNS (Europe, Global)
}

dns_record_types = {
    'A': 1,
    'NS': 2,
    'CNAME': 5,
    'SOA': 6,
    'PTR': 12,
    'MX': 15,
    'TXT': 16,
    'AAAA': 28,
    'SRV': 33,
    'NAPTR': 35,
    'KX': 36,
    'CERT': 37,
    'DNAME': 39,
    'DS': 43,
    'SSHFP': 44,
    'IPSECKEY': 45,
    'RRSIG': 46,
    'NSEC': 47,
    'DNSKEY': 48,
    'DHCID': 49,
    'NSEC3': 50,
    'NSEC3PARAM': 51,
    'TLSA': 52,
    'SMIMEA': 53,
    'HIP': 55,
    'CDS': 59,
    'CDNSKEY': 60,
    'OPENPGPKEY': 61,
    'CSYNC': 62,
    'ZONEMD': 63,
    'SVCB': 64,
    'HTTPS': 65,
    'SPF': 99,
    'EUI48': 108,
    'EUI64': 109,
    'TKEY': 249,
    'TSIG': 250,
    'URI': 256,
    'CAA': 257,
    'AVC': 260
}

Key_vault = []
#next version i will also empty it.

#Classes for DNSMessage.
#Anser and Question class.
#Just to make it easy to use.
class Anser():
    def __init__(self, domain:str, type:int, Class:int, ttl:int, data:bytes) -> None:
        self.domain = domain
        self.type = type
        self.Class = Class
        self.ttl = ttl

        
        
        self.data = data
    def __str__(self) -> str:
        return f"Anser: {self.domain} {self.type} {self.Class} {self.ttl} {self.data}"
    def ToTuple(self):
        return tuple(self.domain, self.type, self.Class, self.ttl, self.data)

def KEYTOVALUE(dict: dict, value):
    for key, val in dict.items():
        if val == value:
            return key
    return None

class Question():
    def __init__(self, domain:str, type:int, Class:int) -> None:
        self.domain = domain
        self._type = type
        self.Class = Class
    def __str__(self) -> str:
        return f"Question: {self.domain} {self.type} {self.Class}"
    
    @property
    def type(self):
        return self._type

class DNSMessage():
    def __init__(self, **kwargs) -> None:
        self.id = kwargs.get("id", None)
        if not self.id:
            while True: #just for case to not get same key
                key_ = format(random.randint(0, 0xFFFF), '04X')
                if key_ not in Key_vault:
                    Key_vault.append(key_)
                    self.id = key_
                    break
        self.QR = kwargs.get("qr") #must to be suplied
        self.OPcode = 0#normal query #rest are useless for this cleint.(0-5)
        self.AA = 0
        self.TC = 0 #this code dont support TrunCation. TC= it will send few response as its to large for UDP.(never saw this).
        self.RD = kwargs.get("rd", 1)
        self.RA = kwargs.get("ra", 0) #Only in response os -_-
        self.Z = 000 #This part is saved for future use. its 3 0 bits(000)
        self.RCcode = kwargs.get("rcode", 0)
        self._questions = kwargs.get("Q", []) #List of tupels in this format: `("address", "type", "class")` #type is question type.
        self.QN = len(self._questions) #number of questions
        self._ansers = kwargs.get("A", []) #ansers in this format: `("address", "type", "class", "ttl", "data")` #type is question type.
        self.AN = len(self._ansers) #number of ansers
        self.NScount = 0 #This project dont use this.
        self.ARcount = 0 #This project dont use this.
        self.NotFine = kwargs["!"] #to check if its got any error or not. if its True its mean it got error. and it will not save in Memory.
        #Use this Class after sing Parse(to parse the data to json For this class).
    
    #Parse funcions.
    def HeadersToBytes(self) -> bytes:
        #Convert the headers to bytes.
        flags = (self.QR << 15) | (self.OPcode << 11) | (self.AA << 10) | (self.TC << 9) | (self.RD << 8) | (self.RA << 7) | (self.Z << 4) | self.RCcode
        id_bytes = bytes.fromhex(self.id)
        flags_bytes = flags.to_bytes(2, byteorder='big')
        QN_bytes = self.QN.to_bytes(2, byteorder='big')
        AN_bytes = self.AN.to_bytes(2, byteorder='big')
        NScount_bytes = self.NScount.to_bytes(2, byteorder='big')
        ARcount_bytes = self.ARcount.to_bytes(2, byteorder='big')
        return id_bytes + flags_bytes + QN_bytes + AN_bytes + NScount_bytes + ARcount_bytes

    def QuestionToBytes(self, X:int=0) -> bytes:
        msg = b""
        pointers = {}
        for q in self._questions:
            pointers[q[0]] = len(msg) + X
            msg += DomainToBytes(q[0]) + b"\x00" + q[1].to_bytes(2, byteorder='big') + q[2].to_bytes(2, byteorder='big')
        return msg, pointers
    def AnsersToBytes(self, X:int=0, pointers:dict={}):
        msg = b""
        for an in self._ansers:
            rdata = RdataToBytes(an[1],an[4])
            if an[0] in pointers.keys():
                pointer = pointers[an[0]]
                msg += (0xc000 | pointer).to_bytes(2, byteorder='big') + an[1].to_bytes(2, byteorder='big') + an[2].to_bytes(2, byteorder='big') + an[3].to_bytes(4, byteorder='big') + len(rdata).to_bytes(2, byteorder='big') + rdata
                continue
            msg += DomainToBytes(an[0]) + an[1].to_bytes(2, byteorder='big') + an[2].to_bytes(2, byteorder='big') + an[3].to_bytes(4, byteorder='big') + len(rdata).to_bytes(2, byteorder='big') + rdata
        return msg, pointers
    def AnserToBytes(self) -> bytes:
        msg = b""
        msg += self.HeadersToBytes()
        x = 12
        question_part, pointers = self.QuestionToBytes(x)
        msg += question_part
        x += len(question_part)
        anser_part, pointers = self.AnsersToBytes(x, pointers)
        msg += anser_part
        return msg
            
    def QueryToBytes(self) -> bytes:
        msg = b""
        msg += self.HeadersToBytes()
        question_part, x = self.QuestionToBytes()
        msg += question_part
        return msg
    
    def ToBytes(self) -> bytes:
        if self.QR == 0:
            return self.QueryToBytes()
        if self.QR == 1:
            return self.AnserToBytes()
        return False #?
        #Convert the class to bytes.(query/response depends on the QR flag) 
    
    #Funcions to get the anser and questions.
    def GetAnsers(self) -> List[Anser]:
        _ansers = []
        for anser in self._ansers:
            _ansers.append(Anser(*anser))
        return _ansers
    
    def GetQuestions(self) -> List[Question]:
        _questions = []
        for question in self._questions:
            _questions.append(Question(*question))
        return _questions

def BuildAnser(requests: DNSMessage, anser: list, AA: int) -> DNSMessage:
    #requests is the DNSMessage object. and anser is the anser list.
    requests.AN = len(anser)
    requests.QR = 1
    requests.RA = 1
    requests.AA = AA
    requests.RD = 1
    requests._ansers = anser
    return requests

def ParseDomain(data: bytes, msg:bytes):
    domain = ""
    x = 0
    while True:
        len_ = data[x]
        if len_ == 192: #c0 its a pointer! its mean it will point to other location in message.
            domain += ParseDomain(msg[data[x+1]:], msg) #it is possible to be (part_of_domain) (pointer) (another_part)
            return domain
        if len_ == 0:
            break
        domain += data[x+1:x+1+len_].decode() + "."
        x += len_ + 1
    return domain[:-1]

def parse_type_a_rdata(rdata, msg):
    # Parse RDATA for Type A (IPv4 address)
    return ".".join([str(byte) for byte in rdata]) #normal IPv4 address 4digit with `.`

def parse_type_ns_rdata(rdata, msg):
    # Parse RDATA for Type NS (name server)
    #normal domain so:
    return ParseDomain(rdata, msg)

def parse_type_cname_rdata(rdata, msg):
    # Parse RDATA for Type CNAME (canonical name)
    #normal domain so:
    return ParseDomain(rdata, msg)

def parse_type_soa_rdata(rdata, msg):
    # To be honest i dont know what is this. so i will just return the data.
    return rdata

def parse_type_ptr_rdata(rdata, msg):
    # Parse RDATA for Type PTR (pointer)
    #normal domain so:
    return ParseDomain(rdata, msg)

def parse_type_mx_rdata(rdata, msg):
    # Parse RDATA for Type MX (mail exchange)
    #mail exchange so:
    return {"priority": rdata[2],"target": ParseDomain(rdata[2:], msg)}


def parse_type_txt_rdata(rdata, msg):
    # Parse RDATA for Type TXT (text)
    length = rdata[0]
    return rdata[1:1 + length].decode()

def parse_type_aaaa_rdata(rdata, msg):
    #IPv6 address.
    return socket.inet_ntop(socket.AF_INET6, rdata)#using socket funcion to convert to IPv6 address because its weird format.

def parse_type_srv_rdata(rdata, msg):
    # Parse RDATA for Type SRV (service)
    #To be honest i dont know what is this. so i will just return the data.
    return rdata

def parse_type_spf_rdata(rdata, msg):
    # Parse RDATA for Type SPF (sender policy framework)
    length = rdata[0]
    return rdata[1:1 + length].decode()

# Map RR types to parsing functions, sorted by RR type ID
rr_type_parsers = {
    1: parse_type_a_rdata,       # Type A
    2: parse_type_ns_rdata,      # Type NS
    5: parse_type_cname_rdata,   # Type CNAME
    6: parse_type_soa_rdata,     # Type SOA
    12: parse_type_ptr_rdata,    # Type PTR
    15: parse_type_mx_rdata,     # Type MX
    16: parse_type_txt_rdata,    # Type TXT
    28: parse_type_aaaa_rdata,   # Type AAAA
    33: parse_type_srv_rdata,    # Type SRV
    99: parse_type_spf_rdata     # Type SPF
}
##############################################################################################################################
##############################################################################################################################
##############################################################################################################################

def DomainToBytes(domain: str) -> bytes:
    msg = b""
    for part in domain.split("."):
        msg += bytes([len(part)]) + part.encode()
    return msg

#Unparse(Rdata to data).
def unparse_type_a_rdata(data):
    # Unparse data for Type A (IPv4 address)
    ip = b""
    for part in data.split("."):
        ip += bytes([int(part)])
    return ip

def unparse_type_ns_rdata(data):
    # Unparse data for Type NS (name server)
    return DomainToBytes(data)

def unparse_type_cname_rdata(data):
    # Unparse data for Type CNAME (canonical name)
    return DomainToBytes(data)

def unparse_type_soa_rdata(data):
    # Unparse data for Type SOA (start of authority)
    # To be honest, I don't know the format of SOA data, so returning the data as is
    return data

def unparse_type_ptr_rdata(data):
    # Unparse data for Type PTR (pointer)
    return DomainToBytes(data)

def unparse_type_mx_rdata(data):
    # Unparse data for Type MX (mail exchange)
    return bytes([data["priority"]]) + DomainToBytes(data["target"])

def unparse_type_txt_rdata(data):
    # Unparse data for Type TXT (text)
    return bytes([len(data)]) + data.encode()

def unparse_type_aaaa_rdata(data):
    # Unparse data for Type AAAA (IPv6 address)
    return socket.inet_pton(socket.AF_INET6, data)

def unparse_type_srv_rdata(data):
    # Unparse data for Type SRV (service)
    # To be honest, I don't know the format of SRV data, so returning the data as is
    return data

def unparse_type_spf_rdata(data):
    # Unparse data for Type SPF (sender policy framework)
    return bytes([len(data)]) + data.encode()

# Map RR types to unparsing functions, sorted by RR type ID
rr_type_unparsers = {
    1: unparse_type_a_rdata,       # Type A
    2: unparse_type_ns_rdata,      # Type NS
    5: unparse_type_cname_rdata,   # Type CNAME
    6: unparse_type_soa_rdata,     # Type SOA
    12: unparse_type_ptr_rdata,    # Type PTR
    15: unparse_type_mx_rdata,     # Type MX
    16: unparse_type_txt_rdata,    # Type TXT
    28: unparse_type_aaaa_rdata,   # Type AAAA
    33: unparse_type_srv_rdata,    # Type SRV
    99: unparse_type_spf_rdata     # Type SPF
}

def RdataToBytes(type, rdata):
    return rr_type_unparsers[type](rdata)

def ParseNAME(offset:int, msg:bytes):
    domain = ""
    while True:
        len_ = msg[offset]
        if len_ == 192: #192=c0 = its pointer(in DNS protocol). its mean it will point to other location in message.
            d, _= ParseNAME(msg[offset+1], msg)
            domain += d
            return domain, offset + 1
        if len_ == 0:
            break
        domain += msg[offset+1:offset+1+len_].decode() + "."
        offset += len_ + 1
    return domain[:-1], offset + 1

class Parse():
    async def DNSMessageToJSON(msg : bytes) -> DNSMessage:
        _ = {}
        _["id"] = msg[:2].hex()
        _["!"] = False
        #flags part:
        flags = int.from_bytes(msg[2:4], byteorder='big')  # Taking 16 bits (2 bytes) from index 2 to 3
        _["qr"] = (flags >> 15) & 0x1  # QR bit (1 bit)
        _["opcode"] = (flags >> 11) & 0xF  # Opcode (4 bits)
        _["aa"] = (flags >> 10) & 0x1  # Authoritative Answer (1 bit)
        _["tc"] = (flags >> 9) & 0x1  # Truncated (1 bit)
        _["rd"] = (flags >> 8) & 0x1  # Recursion Desired (1 bit)
        _["ra"] = (flags >> 7) & 0x1  # Recursion Available (1 bit)
        _["z"] = (flags >> 4) & 0x7  # Reserved (3 bits)
        _["rcode"] = flags & 0xF  # Response code (4 bits)
        _["QN"] = int.from_bytes(msg[4:6], byteorder='big')
        _["AN"] = int.from_bytes(msg[6:8], byteorder='big')
        
        #Questions part:
        _["Q"] = []
        x = 12
        for I in range(_["QN"]):
            try:
                domain, x = ParseNAME(x, msg)
            except:
                _["!"] = True
                return DNSMessage(**_)
            type = int.from_bytes(msg[x:x+2], byteorder='big')
            Class = int.from_bytes(msg[x+2:x+4], byteorder='big')
            _["Q"].append((domain, type, Class))
            x += 4
        #Anser part:
        _["A"] = []
        for I in range(_["AN"]):
            try:
                domain, x = ParseNAME(x, msg)
            except:
                _["!"] = True
                return DNSMessage(**_)
            x += 1
            type = int.from_bytes(msg[x:x+2], byteorder='big')
            Class = int.from_bytes(msg[x+2:x+4], byteorder='big')
            ttl = int.from_bytes(msg[x+4:x+8], byteorder='big')
            rdlength = int.from_bytes(msg[x+8:x+10], byteorder='big')
            x += 10
            try:
                data = rr_type_parsers[type](msg[x:x+rdlength], msg)
            except:
                _["!"] = True
                return DNSMessage(**_)
            x += rdlength
            _["A"].append((domain, type, Class, ttl, data))
        return DNSMessage(**_)
    
class Events():
    def __init__(self):
        self._flag = False
        self._waiters = deque()

    async def wait(self):
        if self._flag:
            return
        
        loop = self.get_event_loop()
        fut = loop.create_future()
        self._waiters.append(fut)
        await fut

    def set(self):
        self._flag = True
        while self._waiters:
            waiter = self._waiters.popleft()
            waiter.set_result(None)

    def get_event_loop(self):
        return asyncio.get_running_loop()

memory = {
    "Domain":
        {
            "type": "Type", #Type of the request.
            "class": "Class", #Class of the request.
            "last_update": "date_timestring",#better than same the object so just the datetime
            "anser": [("domain", "type", "Class", "TTL(last_update-TTL)", "data")] #List of tuples
        }
}

#This class is saving the Memory of the DNS request.
#I cant use normal dict because i need to set as Key domain type and class.

class Memory():
    def __init__(self) -> None:
        self.memory = {}
    def UpdateTTL(self, anser, lu):
        anser_ = []
        for an in anser:
            an = list(an)
            an[3] = an[3] - (datetime.datetime.now() - lu).seconds
            if an[3] > 0:
                anser_.append(tuple(an))
        if anser_ == []:
            return False
        return anser_
    
    def Save(self, request: DNSMessage):
        if len(request._questions) != 1:
            return False
        anser = []
        ttl = 4294967295
        for an in request._ansers:
            if ttl > an[3]:
                ttl = an[3]
            anser.append(an)
        self.memory[str(request._questions[0])] = {"TTL": ttl, "AA": request.AA, "last_update": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "anser": anser}
    def Check(self, request: DNSMessage):
        if len(request._questions) != 1:
            return False
        key = str(request._questions[0])
        if key in self.memory:
            if (datetime.datetime.now() - datetime.datetime.strptime(self.memory[key]["last_update"], "%Y-%m-%d %H:%M:%S")).seconds < self.memory[key]["TTL"]:
                return self.UpdateTTL(self.memory[key]["anser"],datetime.datetime.strptime(self.memory[key]["last_update"], "%Y-%m-%d %H:%M:%S")), self.memory[key]["AA"]
            else:
                del self.memory[key]
        return False, 0
    
memory = Memory()

NetworkMemory = psutil.net_connections(kind='inet')
#This funcion will not call the psutil net connection every time.
#It will save it and call just if not found the port.
def GetProcessName(port):
    global NetworkMemory
    for conn in NetworkMemory:
        if conn.laddr.port == port:
            return conn.pid, psutil.Process(conn.pid).name()
    NetworkMemory = psutil.net_connections(kind='inet')
    for conn in NetworkMemory:
        if conn.laddr.port == port:
            return conn.pid, psutil.Process(conn.pid).name()
    return None, None

#Funcion TO Convert addr(ip, port). To string.
def GetAddrString(addr: tuple):
    """
    If its local machine ip. it will get process name. if not return just ip:port.
    """
    if addr[0] == My_IP:
        PID, name = GetProcessName(addr[1])
        if PID != None and name != None:
            return f"LocalHost:{addr[1]} - Process: (Pid:{PID}, Name:{name})", name
        return f"LocalHost:{addr[1]} - Process: None", None
    return f"{addr[0]}:{addr[1]}", None

def Domain(dom):
    pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    if re.match(pattern, dom):
        return True
    else:
        return False
    
def SetToString(time):
    if time < 1:
        return f"{int(time*1000)}ms"
    if time < 60:
        return f"{int(time)}s"
    if time < 3600:
        return f"{int(time/60)}m"
    return f"{int(time/3600)}h"

#co-pilot is him!
#Ty for the code.
#+math is trash.
def BytesParse(B):
    """Return the given bytes as a human-friendly KB, MB, GB, or TB string."""
    B = float(B)
    KB = float(1024)
    MB = float(KB ** 2)  # 1,048,576
    GB = float(KB ** 3)  # 1,073,741,824
    TB = float(KB ** 4)  # 1,099,511,627,776

    if B < KB:
        return '{0} {1}'.format(B, 'Bytes' if 0 == B > 1 else 'Byte')
    elif KB <= B < MB:
        return '{0:.2f} KB'.format(B / KB)
    elif MB <= B < GB:
        return '{0:.2f} MB'.format(B / MB)
    elif GB <= B < TB:
        return '{0:.2f} GB'.format(B / GB)
    elif TB <= B:
        return '{0:.2f} TB'.format(B / TB)

def get_country_location(country_code):
    import pycountry
    country = pycountry.countries.get(alpha_2=country_code)
    print(country)
    if country:
        return country.name, country.latitude, country.longitude
    else:
        return None, None, None
    
def euclidean_distance(lat1, lon1, lat2, lon2):
    return ((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) ** 0.5

def find_nearest_country(target_lat, target_lon, country_list):
    nearest_country = None
    min_distance = float('inf')

    for country_code in country_list:
        _, country_lat, country_lon = get_country_location(country_code)
        if country_lat is None or country_lon is None:
            print(f"Invalid country code: {country_code}")
            continue

        distance = euclidean_distance(target_lat, target_lon, country_lat, country_lon)
        if distance < min_distance:
            min_distance = distance
            nearest_country = country_code

    return nearest_country


def is_private_ip(ip):
    octets = ip.split('.')
    if len(octets) != 4:
        return False
    try:
        octets = list(map(int, octets))
    except ValueError:
        return False
    if (octets[0] == 10):
        return True
    elif (octets[0] == 172 and 16 <= octets[1] <= 31):
        return True
    elif (octets[0] == 192 and octets[1] == 168):
        return True
    elif (octets[0] == 169 and octets[1] == 254):
        return True
    
    return False