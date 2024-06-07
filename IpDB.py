#This File is from the IP2Location Python Library. It is used to get the country of the IP address.
import sys
import struct
import socket
import os
from re import match

MAX_IPV4_RANGE = 4294967295
MAX_IPV6_RANGE = 340282366920938463463374607431768211455

_COUNTRY_POSITION = (0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2)

def u(x):
    if isinstance(x, bytes):
        return x.decode()
    return x
def b(x):
    if isinstance(x, bytes):
        return x
    return x.encode('ascii')

# Windows version of Python does not provide it
# for compatibility with older versions of Windows.
if not hasattr(socket, 'inet_pton'):
    def inet_pton(t, addr):
        import ctypes
        a = ctypes.WinDLL('ws2_32.dll')
        in_addr_p = ctypes.create_string_buffer(b(addr))
        if t == socket.AF_INET:
            out_addr_p = ctypes.create_string_buffer(4)
        elif t == socket.AF_INET6:
            out_addr_p = ctypes.create_string_buffer(16)
        n = a.inet_pton(t, in_addr_p, out_addr_p)
        if n == 0:
            raise ValueError('Invalid address')
        return out_addr_p.raw
    socket.inet_pton = inet_pton

def is_ipv4(ip):
    if '.' in ip:
        ip_parts = ip.split('.')
        if len(ip_parts) == 4:
            for i in range(0,len(ip_parts)):
                if str(ip_parts[i]).isdigit():
                    if int(ip_parts[i]) > 255:
                        return False
                else:
                    return False
            pattern = r'^([0-9]{1,3}[.]){3}[0-9]{1,3}$'
            if match(pattern, ip) is not None:
                return 4
        else:
            return False
    else:
        return False
    return False

class IP2LocationRecord:
    ip = None
    country_short = None
    country_long = None
    
    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return repr(self.__dict__)

class IP2Location(object):
    ''' IP2Location database '''

    def __init__(self, filename=None,mode='FILE_IO'):
        ''' Creates a database object and opens a file if filename is given
            
        '''
        self.mode = mode
        
        if filename is not None:
            if os.path.isfile(filename) == False:
                raise ValueError("The database file does not seem to exist.")
        
        if filename:
            self.open(filename)

    def open(self, filename):
        ''' Opens a database file '''
        # Ensure old file is closed before opening a new one
        self.close()

        if (self.mode == 'SHARED_MEMORY'):
            import mmap
            db1 = open(filename, 'r+b')
            self._f = mmap.mmap(db1.fileno(), 0)
            db1.close()
            del db1
        elif (self.mode == 'FILE_IO'):
            self._f = open(filename, 'rb')
        else:
            raise ValueError("Invalid mode. Please enter either FILE_IO or SHARED_MEMORY.")
        if (self.mode == 'SHARED_MEMORY'):
            # We can directly use slice notation to read content from mmap object. https://docs.python.org/3/library/mmap.html?highlight=mmap#module-mmap
            header_row = self._f[0:32]
        else:
            self._f.seek(0)
            header_row = self._f.read(32)
        self._dbtype = struct.unpack('B', header_row[0:1])[0]
        self._dbcolumn = struct.unpack('B', header_row[1:2])[0]
        self._dbyear = struct.unpack('B', header_row[2:3])[0]
        self._dbmonth = struct.unpack('B', header_row[3:4])[0]
        self._dbday = struct.unpack('B', header_row[4:5])[0]
        self._ipv4dbcount = struct.unpack('<I', header_row[5:9])[0]
        self._ipv4dbaddr = struct.unpack('<I', header_row[9:13])[0]
        self._ipv6dbcount = struct.unpack('<I', header_row[13:17])[0]
        self._ipv6dbaddr = struct.unpack('<I', header_row[17:21])[0]
        self._ipv4indexbaseaddr = struct.unpack('<I', header_row[21:25])[0]
        self._ipv6indexbaseaddr = struct.unpack('<I', header_row[25:29])[0]
        self._productcode = struct.unpack('B', header_row[29:30])[0]
        self._licensecode = struct.unpack('B', header_row[30:31])[0]
        self._databasesize = struct.unpack('B', header_row[31:32])[0]
        if (self._productcode != 1) :
            if (self._dbyear > 20 and self._productcode != 0) :
                self._f.close()
                del self._f
                raise ValueError("Incorrect IP2Location BIN file format. Please make sure that you are using the latest IP2Location BIN file.")

    def close(self):
        if hasattr(self, '_f'):
            # If there is file close it.
            self._f.close()
            del self._f

    def get_country_short(self, ip):
        ''' Get country_short '''
        rec = self.get_all(ip)
        return rec and rec.country_short
    def get_country_long(self, ip):
        ''' Get country_long '''
        rec = self.get_all(ip)
        return rec and rec.country_long
    
    def get_all(self, addr):
        ''' Get the whole record with all fields read from the file

            Arguments:

            addr: IPv4 or IPv6 address as a string
     
            Returns IP2LocationRecord or None if address not found in file
        '''
        return self._get_record(addr)

    def _reads(self, offset):
        self._f.seek(offset - 1)
        ''''''
        data = self._f.read(257)
        char_count = struct.unpack('B', data[0:1])[0]
        string = data[1:char_count+1]
        if sys.version < '3':
            return str(string.decode('iso-8859-1').encode('utf-8'))
        else :
            return u(string.decode('iso-8859-1').encode('utf-8'))

    def _readi(self, offset):
        self._f.seek(offset - 1)
        # return struct.unpack('<I', self._f.read(4))[0]
        return struct.unpack('<L', self._f.read(4))[0]

    def _readip(self, offset, ipv):
        if ipv == 4:
            return self._readi(offset)
        elif ipv == 6:
            a, b, c, d = self._readi(offset), self._readi(offset + 4), self._readi(offset + 8), self._readi(offset + 12) 
            return (d << 96) | (c << 64) | (b << 32) | a

    def _readips(self, offset, ipv):
        if ipv == 4:
            return socket.inet_ntoa(struct.pack('!L', self._readi(offset)))
        elif ipv == 6:
            return str(self._readip(offset, ipv))

    def _read_record(self, mid, ipv):
        rec = IP2LocationRecord()

        if ipv == 4:
            off = 0
            baseaddr = self._ipv4dbaddr
            dbcolumn_width = self._dbcolumn * 4 + 4
        elif ipv == 6:
            off = 12
            baseaddr = self._ipv6dbaddr
            dbcolumn_width = self._dbcolumn * 4

        def calc_off(what, mid):
            return baseaddr + mid * (self._dbcolumn * 4 + off) + off + 4 * (what[self._dbtype]-1)

        if (self.mode == 'SHARED_MEMORY'):
            # We can directly use slice notation to read content from mmap object. https://docs.python.org/3/library/mmap.html?highlight=mmap#module-mmap
            raw_positions_row = self._f[ (calc_off(_COUNTRY_POSITION, mid)) - 1 : (calc_off(_COUNTRY_POSITION, mid)) - 1 + dbcolumn_width]
        else:
            self._f.seek((calc_off(_COUNTRY_POSITION, mid)) - 1)
            raw_positions_row = self._f.read(dbcolumn_width)

        if self.original_ip != '':
            rec.ip = self.original_ip
        else:
            rec.ip = self._readips(baseaddr + (mid) * self._dbcolumn * 4, ipv)

        if _COUNTRY_POSITION[self._dbtype] != 0:
            rec.country_short = self._reads(struct.unpack('<I', raw_positions_row[0 : ((_COUNTRY_POSITION[self._dbtype]-1) * 4)])[0] + 1)
            rec.country_long =  self._reads(struct.unpack('<I', raw_positions_row[0 : ((_COUNTRY_POSITION[self._dbtype]-1) * 4)])[0] + 4)

        return rec

    def read32x2(self, offset):
        self._f.seek(offset - 1)
        data = self._f.read(8)
        return struct.unpack('<L', data[0:4])[0], struct.unpack('<L', data[4:8])[0]

    def readRow32(self, offset):
        data_length = self._dbcolumn * 4 + 4
        self._f.seek(offset - 1)
        raw_data = self._f.read(data_length)
        ip_from = struct.unpack('<L', raw_data[0:4])[0]
        ip_to = struct.unpack('<L', raw_data[data_length-4:data_length])[0]
        return (ip_from, ip_to)

    def _parse_addr(self, addr): 
        ''' Parses address and returns IP version. Raises exception on invalid argument '''
        ipv = 0
        ipnum = -1
        if is_ipv4(addr) == 4 and '256' not in addr:
            try:
                # ipnum = int(ipaddress.IPv4Address(addr))
                ipnum = struct.unpack('!L', socket.inet_pton(socket.AF_INET, addr))[0]
                ipv = 4
            except (socket.error, OSError, ValueError):
                ipv = 0
                ipnum = -1
        return ipv, ipnum
        
    def _get_record(self, ip):
        self.original_ip = ip
        low = 0
        ipv, ipnum = self._parse_addr(ip)
        if ipv == 4:
            if (ipnum == MAX_IPV4_RANGE):
                ipno = ipnum - 1
            else:
                ipno = ipnum
            baseaddr = self._ipv4dbaddr
            high = self._ipv4dbcount
            if self._ipv4indexbaseaddr > 0:
                indexpos = ((ipno >> 16) << 3) + self._ipv4indexbaseaddr
                low,high = self.read32x2(indexpos)
            while low <= high:
                mid = int((low + high) / 2)
                if ipv == 4:
                    ipfrom, ipto = self.readRow32(baseaddr + mid * self._dbcolumn * 4 )
                if ipfrom <= ipno < ipto:
                    return self._read_record(mid, ipv)
                else:
                    if ipno < ipfrom:
                        high = mid - 1
                    else:
                        low = mid + 1
        else:
            return None