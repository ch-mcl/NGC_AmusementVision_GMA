import os
import sys

import struct

from .gcmf import Gcmf


#Messages
MSG_INFO_DATA = '{0}: {1}'
MSG_INFO_DATA_HEX = '{0}: {1:#X}'

CHAR_SET = 'ascii'

#GCMF Entry Offset
class GmaEntryOffset:
    fmt = '2i'
    
    def __init__(self):
        self.offset_gcmf = 0
        self.offset_name = 0
        
    def unpack(self, file, endian):
        bytes = file.read(struct.calcsize(self.fmt))
        buff = struct.unpack_from(endian + self.fmt, bytes, 0)
        self.offset_gcmf = buff[0]
        self.offset_name = buff[1]

    def pack(self, file, endian):
        buff = struct.pack(endian + self.fmt, self.offset_gcmf, self.offset_name)
        file.write(buff)


#GCMF Entry
class GcmfEntry:
    def __init__(self):
        self.gcmf = Gcmf()
        self.name = ''
        
    #read String
    def read_string(self, file):
        offset = file.tell()
        string = ''
        while (True):
            file.seek(offset)
            char_raw = file.read(1)
            char = char_raw.decode(CHAR_SET)
            
            if char_raw == b'\x00':
                file.seek(file.tell()-1)
                return string
            else:
                string += str(char)
                offset = offset + 1
    
    def unpack(self, file, offset_gcmf, offset_name, endian):
        seek_pos = file.tell()
        file.seek(offset_gcmf)
        self.gcmf.unpack(file, endian)
        file.seek(offset_name)
        self.name = self.read_string(file)
        file.seek(seek_pos)


#GMA file structure
class Gma:
    fmt = '2i'
    
    def __init__(self):
        self.count = 0
        self.base_gcmf = 0
        self.base_name = 0
        self.entry_offsets = []
        self.entrys = []

# 1: file stream
# 2: endian
#     >: Big Endian
#     <: Little Endian
    def unpack(self, file, endian):
        bytes = file.read(struct.calcsize(self.fmt))
        buff = struct.unpack_from(endian + self.fmt, bytes, 0)
        
        self.count = buff[0]
        print(MSG_INFO_DATA.format('GCMF Count', self.count))
        self.base_gcmf = buff[1]
        
        #get entry_offset
        for i in range(self.count):
            entry_offset = GmaEntryOffset()
            entry_offset.unpack(file, endian)
            self.entry_offsets.append(entry_offset)

        #get entry
        self.base_name = file.tell()
        for i in range(self.count):
            entry = GcmfEntry()
            offset = self.entry_offsets[i]
            if offset.offset_gcmf != -1 or offset.offset_name != 0:
                offset_gcmf = self.base_gcmf + offset.offset_gcmf
                offset_name = self.base_name + offset.offset_name
                entry.unpack(file, offset_gcmf, offset_name, endian)
            self.entrys.append(entry)
        
    def pack(self, file, endian):
        self.count = len(self.entrys)
        #skip Header(8), and Gcmf Entry(count * 8)
        self.base_name = struct.calcsize(self.fmt) + (self.count * 0x08)
        file.seek(self.base_name)
        print( MSG_INFO_DATA_HEX.format('gcmf_name_offset', file.tell()) )
        str_len = 0x00
        #Object Names
        for entry in self.entrys:
            entry_offset = GmaEntryOffset()
            entry_offset.offset_name = str_len
            self.entry_offsets.append(entry_offset)
            string = entry.name
            fmt = endian + '{}s'.format(len(string))
            buff = struct.pack(fmt, bytes(string.encode(CHAR_SET)))
            file.write(buff)
            #Padding
            file.write(bytes(1))
            while (file.tell() % 4) != 0x00:
                file.write(bytes(1))
            str_len = file.tell() - self.base_name
        #Padding
        while (file.tell() % 0x20 != 0x00):
            file.write(bytes(1))
        
        self.base_gcmf = file.tell()
        
        #GCMF object
        for (entry, entry_offset) in zip(self.entrys, self.entry_offsets):
            #Store gcmf offset
            offset_gcmf = file.tell() - self.base_gcmf
            entry_offset.offset_gcmf = offset_gcmf
            #Write Gcmf
            entry.gcmf.pack(file, endian)

        #GCMF Entry Offset
        file.seek(0x08)
        print( MSG_INFO_DATA_HEX.format('entry offset', len(self.entry_offsets)) )
        for entry_offset in self.entry_offsets:
            entry_offset.pack(file, endian)
        
        file.seek(0x00)
        buff = struct.pack(endian + self.fmt, self.count, self.base_gcmf)
        file.write(buff)
        