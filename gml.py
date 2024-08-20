import os
import sys

import struct

from .gcmf import Gcmf


#Messages
MSG_INFO_DATA = '{0}: {1}'
MSG_INFO_DATA_HEX = '{0}: {1:#X}'

CHAR_SET = 'ascii'

#GCMF Entry Offset
class GmlEntryOffset:
    fmt = '4i'
    
    def __init__(self):
        self.offset_gcmf = 0x00
        self.gcmf_size = 0x00
        self.offset_name = 0x00
        
    def unpack(self, file, endian):
        bytes = file.read(struct.calcsize(self.fmt))
        buff = struct.unpack_from(endian + self.fmt, bytes, 0)
        self.offset_gcmf = buff[0]
        self.gcmf_size = buff[1]
        self.offset_name = buff[2]

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
class Gml:
    fmt = '8i'
    
    def __init__(self):
        self.count = 0x00
        self.gcmf_name_offset = 0x00
        self.gcmf_name_size = 0x00
        self.unk0x0C = 0x00
        self.unk0x10 = 0x00
        self.unk0x14 = 0x00
        self.unk0x18 = 0x00
        self.unk0x1C = 0x00
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
        self.gcmf_name_offset = buff[1]
        self.gcmf_name_size = buff[2]
        
        #get entry_offset
        for i in range(self.count):
            entry_offset = GmlEntryOffset()
            entry_offset.unpack(file, endian)
            self.entry_offsets.append(entry_offset)

        #get entry
        self.base_name = file.tell()
        for i in range(self.count):
            entry = GcmfEntry()
            offset = self.entry_offsets[i]
            if offset.offset_gcmf != -1 or offset.offset_name != 0:
                offset_gcmf = offset.offset_gcmf
                offset_name = self.gcmf_name_offset + offset.offset_name
                entry.unpack(file, offset_gcmf, offset_name, endian)
            self.entrys.append(entry)