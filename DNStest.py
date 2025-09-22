from DNSClient import DNSClient
import time
import random
import asyncio
import traceback
from util import *

r"""
TY to CHAT to write this files description.
LOL"""

# Strings to generate random domains
Strings = 'abcdefghijklmnopqrstuvwxyz0123456789'

Services_list = [
    "Microsoft",
    "Google",
    "Facebook",
    "Amazon",
    "Youtube",
]
# Generate a random .com domain with a random service
def Dotcom():
    return ''.join(random.choices(Strings, k=10)) + "." + random.choice(Services_list) +".com"

# Generate a random .test domain
def RandomDomain():
    return ''.join(random.choices(Strings, k=10)) + ".test"

# Measure uncached response time
async def uncached_Time(DNS: DNSClient, Count: int = 100):
    uncached_time = 0
    SleepCounter = 0
    for _ in range(Count):
        domain = RandomDomain()
        Query = await DNS.BuildQuery(domain=domain)
        start = time.time()
        try:
            await asyncio.wait_for(DNS.Send(Query.ToBytes()), 1)
        except:
            continue
        end = time.time()
        uncached_time += end - start
        if SleepCounter == 5:
            await asyncio.sleep(0.1)
            SleepCounter = 0
        SleepCounter += 1
    return uncached_time / Count

# Check response times for cached, dotcom, and uncached domains
async def CheckResponseTime(DNS: DNSClient, Count: int = 100):
    cached_time = 0
    dotcom_time = 0
    cached_domains = []

    # Measure uncached time asynchronously

    # Measure dotcom response times
    SleepCounter = 0
    for _ in range(Count):
        domain = Dotcom()
        Query = await DNS.BuildQuery(domain=domain)
        start = time.time()
        #try:
        #    await asyncio.wait_for(DNS.Send(Query.ToBytes()), 1)
        #except:
        #    continue
        try:
            await asyncio.wait_for(DNS.Send(Query.ToBytes()), 0.5)
        except:
            continue
        end = time.time()
        dotcom_time += end - start
        cached_domains.append(domain)
        if SleepCounter == 5:
            await asyncio.sleep(0.1)
            SleepCounter = 0
        SleepCounter += 1
    print("Finished Dotcom")
    # Measure cached response times using previously resolved domains
    for _ in range(Count):
        domain = random.choice(cached_domains)
        Query = await DNS.BuildQuery(domain=domain)
        start = time.time()
        try:
            await asyncio.wait_for(DNS.Send(Query.ToBytes()), 1)
        except:
            continue
        end = time.time()
        cached_time += end - start
        if SleepCounter == 5:
            await asyncio.sleep(0.1)
            SleepCounter = 0
        SleepCounter += 1
    print("Finished Cached")
    # Wait for the uncached task to complete
    uncached_time = await uncached_Time(DNS, Count=Count)
    print("Finished Uncached")
    # Calculate average times
    cached_time /= Count
    dotcom_time /= Count
    return cached_time, dotcom_time, uncached_time

# Main function to initialize the DNS client and check response times
async def SpeedTest(IP: str, Port: int):
    DNS = DNSClient(IP, Port) #Create new client object
    Task = asyncio.create_task(DNS.Reader())
    try:
        Resp = await CheckResponseTime(DNS)
        Task.cancel() #Kill Reader Task.
        return Resp
    except Exception as e:
        print(f"An error occurred: {e}")
        print(traceback.format_exc())