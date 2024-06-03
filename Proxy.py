from util import DNSMessage, Anser, Question, BuildAnser

"""
Filters are convert to python code.
The Objects are:
Anser,Question(Two of the most important.)
DNSmessage,
Funcions:
CMDS(args) #args can be anything. from context:
firts args is the CMD.
msg(DNSmessage) -> DNSmessage object.


Anser()
Keys words:
Block = Block anser
+
Continue #Continue as normal.
Print #Print to Console the anser/question Information.
Wait(Time in seconds.) it will be:
Wait(5) -> Another thing. if its Anser or Block/Continue.


DNSmessage:
DNSmessage is:
class():
process = processname
pid = process pid.
question = return list of Question class.(if its 1 question it will return just object and not list).
anser = return list of Ansers.
the anser part(after ->) type, "data"
#examples:

Q.name = "example.com" & Q.type = 1 -> Block #This will block the anser and return

Q.name = "example.com" -> a, '1.1.1.1'

Q.name == "example.com" & Q.type=28 -> '2606:2800:21f:cb07:6820:80da:af6b:8b2c')

Q.name == "example.com" -> IP6 = '2606:2800:21f:cb07:6820:80da:af6b:8b2c'

Q.name = "example.com" -> CMDS((python.exe "%appdata%\--\python.exe"), msg.ToBytes()) #This will return the anser to the client. with the same anser.

#Anser(after ->) can be only 1 operation.
#its taking first condition. meaning. if you put two conditions that both will return True. it will take the first one.
See it in CheckProxy funcion.
"""
class InvalidType(Exception):
    pass

def anser(IP: str, Type: int, msg: DNSMessage):
    if (len(DNSMessage.GetQuestions()) != 1) and domain == None:
        raise ValueError("Only one question is allowed. When Creating anser. Without domain")
    if domain == None:
        domain = DNSMessage.GetQuestions()[0].name
    anser = Anser(domain, Type, 1, 60, IP)
    DNSMessage._ansers.append(anser)

def cmds(args):
    print(args)
    
AnserFuncions = ["anser", 'cmds']
######################################################
#Funcions:

def FilterToCode(filter: str):
    condition, code = filter.split("->")
    if '&' in condition:
        condition = condition.split("&")
    return condition, code

class Proxy():
    def __init__(self, FileToSave: str):
        self.options = []
        self.writer = open(FileToSave, "a")
        self.reader = open(FileToSave, "r")
        for line in self.reader.readlines():
            try:
                cond, code = FilterToCode(line)
                self.options.append((cond, code))
            except:
                continue
    def CheckProxy(self, msg: DNSMessage):
        Q = msg.GetQuestions()[0]
        for option in self.options:
            conditions, code = option
            if isinstance(conditions, list):
                t = []
                for condition in conditions:
                    t.append(eval(condition))
                t = all(t)
            else:
                t = eval(conditions)
            if t:
                return self.Anser(msg, code)
    def Anser(self, msg: DNSMessage, code: str):
        value = code.replace(" ", '')
        question = msg.GetQuestions()[0]
        ttl = 60#?
        anser1 = [(question.domain, question.type, question.Class, ttl, value)]
        return BuildAnser(msg, anser1, 0)