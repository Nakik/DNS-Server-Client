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

### Example

Below is a simple example demonstrating how to use the DNS client in an asyncio context:

```python
import asyncio
from DNS import DNSServer

async def main():
    dns = DNSServer()
    await dns.Main()

asyncio.run(main())
