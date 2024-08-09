#This file is a logger for the DNS server. It logs the requests and responses.
#Its log them to Console or file. It can be used for debugging.

from util import DNSMessage #Importing the DNSMessage class from util.
import sys
import asyncio
import datetime

class Logger():
    def __init__(self, file: str=None) -> None:
        self.file = file
        self.loop = asyncio.get_event_loop()
        self.Console = sys.stdout
        self.File = open(file, "a") if file else None
        self._X = True

    def GetTime(self):
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    def MsgToString(self, message: DNSMessage):
        #Show just key, question domain and type. and anser number.
        if message.QR == 1:
            if message._questions == []:
                return f"Anser: {message.id} Questions Number: 0 - Ansers Number: {message.AN} Anser Values [{[f"{i[0]} : {i[4]}" for i in message._ansers]}]"
            return f"Anser: {message.id} Questions Number: {message.QN}, ({message._questions[0][0]} {message._questions[0][1]}) - Ansers Number: {message.AN} Anser Values [{[f"{i[0]} : {i[4]}" for i in message._ansers]}]"
        else:
            if message._questions == []:
                return f"Question: {message.id} Questions Number: 0 - Ansers Number: {message.AN}"
            return f"Question: {message.id} Questions Number: {message.QN}, ({message._questions[0][0]} {message._questions[0][1]})"
    async def Print(self, Message) -> None:
        msg = ""
        msg += self.GetTime() + ' - ' + Message
        if self.file:
            self.File.write(msg + '\n')
            self.File.flush()
        else:
            self.Console.write(msg + '\n')

    async def Log(self, message: DNSMessage, AddrString: str, Time=None, Server: str=None) -> None:
        if not self._X:# Part of Inputes class. It is used to stop the logger.
            return False 
        msg = ""
        #TTA = Time To Anser
        msg += self.GetTime() + ' - ' + AddrString + " " + self.MsgToString(message) + (" TTA: " + str(Time) + "ms" if Time else "")
        if Server:
            msg += " - DNS Server: " + Server
        if self.file:
            self.File.write(msg + '\n')
            self.File.flush()
        else:
            self.Console.write(msg + '\n')

if __name__ == "__main__":
    async def main():
        log = Logger()
        await log.Log(DNSMessage(**{"!": False, "id": "\x21\x11", "Q": [("example.com", 1, 1)], "AN": 1, "A": [("example.com", 1, 1, 60, )]}))
        
    asyncio.run(main()) #Run the main function.