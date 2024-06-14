# Python DNS Server and Client

Welcome to the **Python DNS Server and Client** project! This repository provides a comprehensive DNS solution written in Python, allowing you to route all DNS requests through your Python script. The project includes both a server and a client, which can be used to send and receive DNS requests in an asyncio context.

## Features
- **Custom DNS Response Controller**: Allows you to define custom responses for DNS queries, (See Proxy.py for More info).
- **DNS Server**: Proxy To best DNS server based on Machine network connection(DNs servers from Pool in util.py).
- **DNS Client**: An asynchronous DNS client that can send and receive DNS requests using asyncio.
- **Request Routing**: Route all DNS requests through your Python script for custom processing and handling.
- **Asyncio Integration**: Utilize Python's asyncio library for asynchronous DNS operations, providing efficient and scalable DNS query handling.

## example:
![DNS check](https://github.com/Nakik/DNS-Server-Client/blob/main/DNSCheck.png?raw=true)

10.100.102.8 is my Local ip (bind to 0.0.0.0, so you can also access it with public IP :).
## Usage

### DNS Server

The DNS server component allows you to run a custom DNS server, capable of intercepting and handling DNS requests. This can be useful for testing, learning, or implementing custom DNS logic.

### DNS Client

The DNS client component can be used to send DNS queries and process the responses asynchronously. This is particularly useful for applications that require non-blocking DNS resolution.

### Settings
The Settings is json file `Settings.json`
Default settings are:
Port 53<br>
Memory On<br>
Proxy On<br>
Logs File = DNS.log<br>
MemoryLogs 43 sec<br>
DDOs On<br>
DNSQueriesBasedOnLocation On<br>
blockAD On<br>
BlockMalicious On<br>
BlockSuspicious On<br>
BlockAdvertising On<br>

1 means the feature is On, and 0 means it is Off.<br>
Logs - Refers to the file. 0 means logging is off.<br>
MemoryLogs - Refers to time. 0 means memory logging is off.<br>
### Example

Below is a simple example demonstrating how to use the DNS client in an asyncio context:

```python
import asyncio
from DNS import DNSClient

async def main():
    My_IP = My_DNS_IP/8.8.8.8.
    client = DNSClient(My_IP, 53)
    asyncio.create_task(client.Reader()) #Start Reader funcion.
    query = await client.BuildQuery(type=dns_record_types["A"], domain="example.com") #Build query
    TTA = time.time() #Start time
    r = await client.Send(query.ToBytes()) #Send query and wait for response.
    anser = await Parse.DNSMessageToJSON(r) #Parse Response.
    print(f"Time: {SetToString(time.time() - TTA)}\nAnsers:") #Print ansers + Time to anser.
    for ans in anser.GetAnsers():
        print(ans)

asyncio.run(main())
```
This Python DNS project uses the IP2Location LITE database for More info Visit: <a href="https://lite.ip2location.com">IP geolocation</a>.
