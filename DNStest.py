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
    for _ in range(Count):
        domain = RandomDomain()
        Query = await DNS.BuildQuery(domain=domain)
        start = time.time()
        await DNS.Send(Query.ToBytes())
        end = time.time()
        uncached_time += end - start
    return uncached_time / Count

# Check response times for cached, dotcom, and uncached domains
async def CheckResponseTime(DNS: DNSClient, Count: int = 100):
    cached_time = 0
    dotcom_time = 0
    cached_domains = []

    # Measure uncached time asynchronously
    uncached_task = asyncio.create_task(uncached_Time(DNS, Count=Count))

    # Measure dotcom response times
    for _ in range(Count):
        domain = Dotcom()
        Query = await DNS.BuildQuery(domain=domain)
        start = time.time()
        await DNS.Send(Query.ToBytes())
        end = time.time()
        dotcom_time += end - start
        cached_domains.append(domain)

    # Measure cached response times using previously resolved domains
    for _ in range(Count):
        domain = random.choice(cached_domains)
        Query = await DNS.BuildQuery(domain=domain)
        start = time.time()
        await DNS.Send(Query.ToBytes())
        end = time.time()
        cached_time += end - start

    # Wait for the uncached task to complete
    uncached_time = await uncached_task

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