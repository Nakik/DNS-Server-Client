try:
    import winreg, ctypes, os, sys
except:
    raise ImportError #Skill issue. but this libraries are default for python so -_--_-.

class RegisteryEditor():
    def __init__(self):
        self.module = winreg
        self.access = ctypes.windll.shell32.IsUserAnAdmin() == 1
    def ReadKey(self, Path:str, KeyType=winreg.HKEY_LOCAL_MACHINE):
        return self.module.OpenKey(KeyType, Path, 0, winreg.KEY_READ)
    def WriteKey(self, Path:str, KeyType=winreg.HKEY_LOCAL_MACHINE):
        if self.access:
            return self.module.OpenKey(KeyType, Path, 0, winreg.KEY_SET_VALUE)
        else:
            raise PermissionError("Access Denied!")
    def CloseKey(self, Key):
        self.module.CloseKey(Key)
    def GetAllKeys(self, Key):
        num_subkeys, num_values, _ = self.module.QueryInfoKey(Key)
        Keys = {}
        Sub_keys = []
        for i in range(num_values):
            key, value, _ = self.module.EnumValue(Key, i)
            Keys[key] = value
        for i in range(num_subkeys):
            key = self.module.EnumKey(Key, i)
            Sub_keys.append(key)
        return Keys, Sub_keys
    def Write(self, key, Key, value):
        print(key, Key, value)
        self.module.SetValueEx(Key, key, 0, self.module.REG_SZ, value)
def CheckRegistery(MyIp):
    default_Path = r'SYSTEM\CurrentControlSet\Services\Tcpip\Parameters'
    registery = RegisteryEditor()
    key = registery.ReadKey(r'SYSTEM\CurrentControlSet\Services\Tcpip\Parameters')
    WriteKey = registery.WriteKey(r'SYSTEM\CurrentControlSet\Services\Tcpip\Parameters')
    ServersKeys = ["NameServer", "DhcpNameServer"]

    keys, paths = registery.GetAllKeys(key)
    def CheckKeys(keys: list, WriteKey):
        for key in keys:
            if key in ServersKeys:
                registery.Write(key, WriteKey, MyIp)
    CheckKeys(keys.keys(), WriteKey)
    def CheckPath(path: list):
            key = registery.ReadKey(path)
            WriteKey = registery.WriteKey(path)
            keys, NewPath = registery.GetAllKeys(key)
            CheckKeys(keys.keys(), WriteKey)
            for Path in NewPath:
                CheckPath(os.path.join(path,Path))
    for path in paths:
        CheckPath(os.path.join(default_Path,path))

if ctypes.windll.shell32.IsUserAnAdmin() == 0:
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 2)
else:
    try:
        MyIp = sys.argv[1]
    except:
        from DNS import get_local_ip
        MyIp = get_local_ip
    CheckRegistery(MyIp)