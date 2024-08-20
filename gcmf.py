import os
import sys

from ctypes import *
import mathutils
import struct


#Messages
MSG_WARN_NOT_GCMF = 'magic_str:{0} not match magic:{1}'
MSG_INFO_DATA = '{0}: {1}'
MSG_INFO_DATA_HEX = '{0}: {1:#X}'

CHAR_SET = 'ascii'

#Texture Flags 0x00
class Texture_Flags0x00:
    def __init__(self):
        self.unknown0 = False
        self.uv_scroll = False
        self.unknown2 = False
        self.unknown3 = False
        #EnvNormal?
        self.unknown4 = False
        #Load texture images from another tpl
        self.commontex = False
        self.unknown6 = False
        self.unknown7 = False
    
    #Unpack
    def unpack(self, texture_flag):
        if texture_flag >> 0x00 & 0x01 == 0x01:
            self.unknown0 = True
        if texture_flag >> 0x01 & 0x01 == 0x01:
            self.uv_scroll = True
        if texture_flag >> 0x02 & 0x01 == 0x01:
            self.unknown2 = True
        if texture_flag >> 0x03 & 0x01 == 0x01:
            self.unknown3 = True
        if texture_flag >> 0x04 & 0x01 == 0x01:
            self.unknown4 = True
        if texture_flag >> 0x05 & 0x01 == 0x01:
            self.commontex = True
        if texture_flag >> 0x06 & 0x01 == 0x01:
            self.unknown6 = True
        if texture_flag >> 0x07 & 0x01 == 0x01:
            self.unknown7 = True
    
    #Pack
    def pack(self, endian):
        flags = 0x00
        if self.unknown0 == True:
            flags = flags + (0x01 << 0x00)
        if self.uv_scroll == True:
            flags = flags + (0x01 << 0x01)
        if self.unknown2 == True:
            flags = flags + (0x01 << 0x02)
        if self.unknown3 == True:
            flags = flags + (0x01 << 0x03)
        if self.unknown4 == True:
            flags = flags + (0x01 << 0x04)
        if self.commontex == True:
            flags = flags + (0x01 << 0x05)
        if self.unknown6 == True:
            flags = flags + (0x01 << 0x06)
        if self.unknown7 == True:
            flags = flags + (0x01 << 0x07)
        return flags
    

#Texture Mipmap Settings
class Texture_Mipmap:
    def __init__(self):
        self.enable = False
        self.unknown1 = False
        self.unknown2 = False
        self.near = False
        self.unknown4 = False
        self.unknown5 = False
        self.unknown6 = False
        self.unknown7 = False
    
    #Unpack
    def unpack(self, texture_flag):
        if texture_flag >> 0x00 & 0x01 == 0x01:
            self.enable = True
        if texture_flag >> 0x01 & 0x01 == 0x01:
            self.unknown1 = True
        if texture_flag >> 0x02 & 0x01 == 0x01:
            self.unknown2 = True
        if texture_flag >> 0x03 & 0x01 == 0x01:
            self.near = True
        if texture_flag >> 0x04 & 0x01 == 0x01:
            self.unknown4 = True
        if texture_flag >> 0x05 & 0x01 == 0x01:
            self.unknown5 = True
        if texture_flag >> 0x06 & 0x01 == 0x01:
            self.unknown6 = True
        if texture_flag >> 0x07 & 0x01 == 0x01:
            self.unknown7 = True
    
    #Pack
    def pack(self, endian):
        flags = 0x00
        if self.enable == True:
            flags = flags + (0x01 << 0x00)
        if self.unknown1 == True:
            flags = flags + (0x01 << 0x01)
        if self.unknown2 == True:
            flags = flags + (0x01 << 0x02)
        if self.near == True:
            flags = flags + (0x01 << 0x03)
        if self.unknown4 == True:
            flags = flags + (0x01 << 0x04)
        if self.unknown5 == True:
            flags = flags + (0x01 << 0x05)
        if self.unknown6 == True:
            flags = flags + (0x01 << 0x06)
        if self.unknown7 == True:
            flags = flags + (0x01 << 0x07)
        return flags
    
    
#Texture Wrap Flags
class Texture_Wrap:
    def __init__(self):
        self.unknown0 = False
        self.unknown1 = False
        self.repeat_x = False
        self.mirror_x = False
        self.repeat_y = False
        self.mirror_y = False
        self.unknown6 = False
        self.unknown7 = False
    
    #Unpack
    def unpack(self, texture_flag):
        if texture_flag >> 0x00 & 0x01 == 0x01:
            self.unknown0 = True
        if texture_flag >> 0x01 & 0x01 == 0x01:
            self.unknown1 = True
        if texture_flag >> 0x02 & 0x01 == 0x01:
            self.repeat_x = True
        if texture_flag >> 0x03 & 0x01 == 0x01:
            self.mirror_x = True
        if texture_flag >> 0x04 & 0x01 == 0x01:
            self.repeat_y = True
        if texture_flag >> 0x05 & 0x01 == 0x01:
            self.mirror_y = True
        if texture_flag >> 0x06 & 0x01 == 0x01:
            self.unknown6 = True
        if texture_flag >> 0x07 & 0x01 == 0x01:
            self.unknown7 = True
    
    #Pack
    def pack(self, endian):
        flags = 0x00
        if self.unknown0 == True:
            flags = flags + (0x01 << 0x00)
        if self.unknown1 == True:
            flags = flags + (0x01 << 0x01)
        if self.repeat_x == True:
            flags = flags + (0x01 << 0x02)
        if self.mirror_x == True:
            flags = flags + (0x01 << 0x03)
        if self.repeat_y == True:
            flags = flags + (0x01 << 0x04)
        if self.mirror_y == True:
            flags = flags + (0x01 << 0x05)
        if self.unknown6 == True:
            flags = flags + (0x01 << 0x06)
        if self.unknown7 == True:
            flags = flags + (0x01 << 0x07)
        return flags


#GCMF Texture
class Texture:
    fmt = '1h2b1h2b1I1B1b1h1I12x'
    # 1h  2b   1h  2b   1I  1B  1b  1h  1I  12x
    # 0,  1-2, 3,  4-5, 6,  7,  8,  9,  10
    
    def __init__(self):
        self.unk0x00 = Texture_Flags0x00()
        self.mipmap = Texture_Mipmap()
        self.uv_wrap = Texture_Wrap()
        self.texture_index = 0x00
        self.unk0x06 = 0x00
        self.anisotropy = 0x00
        self.unk0x0C = 0x00
        self.is_swappable = False
        self.index = 0x00
        self.unk0x10 = 0x00 #TEV?
        
    def unpack(self, file, endian):       
        bytes = file.read(struct.calcsize(self.fmt))
        buff = struct.unpack_from(endian + self.fmt, bytes, 0)
        
        unk0x00 = buff[0]
        self.unk0x00.unpack(unk0x00)
        mipmap = buff[1]
        self.mipmap.unpack(mipmap)
        uv_wrap = buff[2]
        self.uv_wrap.unpack(uv_wrap)
        self.texture_index = buff[3]
        self.unk0x06 = buff[4]
        self.anisotropy = buff[5]
        #buff[6]
        self.unk0x0C = buff[7]
        is_swappable = buff[8]
        self.index = buff[9]
        self.unk0x10 = buff[10]
        
        if is_swappable & 0x01 == 1:
            self.is_swappable = True
    
    def pack(self, file, endian):
        is_swappable = 0
        if self.is_swappable == True:
            is_swappable = is_swappable + 1
        
        buff = struct.pack(endian + self.fmt, \
                            self.unk0x00.pack(endian), \
                            self.mipmap.pack(endian),  self.uv_wrap.pack(endian), \
                            self.texture_index, self.unk0x06, self.anisotropy, \
                            0, self.unk0x0C, is_swappable, \
                            self.index, self.unk0x10)
        file.write(buff)
        

#GCMF Transform Matrix
class TransformMatrix:
    fmt = '12f'
    
    def __init__(self):
        self.mtx = mathutils.Matrix()
        self.mtx[3][0] = 0.0
        self.mtx[3][1] = 0.0
        self.mtx[3][2] = 0.0
        self.mtx[3][3] = 1.0
    
    def unpack(self, file, endian):
        bytes = file.read(struct.calcsize(self.fmt))
        buff = struct.unpack_from(endian + self.fmt, bytes, 0)
        
        self.mtx[0][0] = buff[0]
        self.mtx[0][1] = buff[1]
        self.mtx[0][2] = buff[2]
        self.mtx[0][3] = buff[3]
        
        self.mtx[1][0] = buff[4]
        self.mtx[1][1] = buff[5]
        self.mtx[1][2] = buff[6]
        self.mtx[1][3] = buff[7]
        
        self.mtx[2][0] = buff[8]
        self.mtx[2][1] = buff[9]
        self.mtx[2][2] = buff[10]
        self.mtx[2][3] = buff[11]
        
    def pack(self, file, endian):
        buff = struct.pack(endian + self.fmt, \
                            self.mtx[0][0], self.mtx[0][1], self.mtx[0][2], self.mtx[0][3], \
                            self.mtx[1][0], self.mtx[1][1], self.mtx[1][2], self.mtx[1][3], \
                            self.mtx[2][0], self.mtx[2][1], self.mtx[2][2], self.mtx[2][3], \
                            )
        file.write(buff)


#GCMF VertexControll
class VertexControll:
    fmt = '5i12x'
       
    def __init__(self):
        self.base_offs = 0x00
        self.count = 0x00
        self.offset_1 = 0x00
        self.offset_2 = 0x00
        self.offset_3 = 0x00
        self.offset_4 = 0x00
    
    def unpack(self, file, endian):
        self.base_offs = file.tell()
        print(MSG_INFO_DATA_HEX.format('VertexControll Offset', self.base_offs))
        
        bytes = file.read(struct.calcsize(self.fmt))
        buff = struct.unpack_from(endian + self.fmt, bytes, 0)
        
        self.count = buff[0]
        self.offset_1 = buff[1]
        self.offset_2 = buff[2]
        self.offset_3 = buff[3]
        self.offset_4 = buff[4]
        print('VertexControll Offset 2: {0:#X} | ABS: {1:#X}'.format(self.offset_2, self.offset_2 + self.base_offs))
        print('VertexControll Offset 3: {0:#X} | ABS: {1:#X}'.format(self.offset_3, self.offset_3 + self.base_offs))


#Vertex Render Flag
class VertexRenderFlag:
    def __init__(self):
        self.dlist0_0 = False
        self.dlist0_1 = False
        self.dlist1_0 = False
        self.dlist1_1 = False
        self.dlist2_0 = False #Exist?
        self.dlist2_1 = False #Exist?
        self.dlist3_0 = False #Exist?
        self.dlist3_1 = False #Exist?
    
    #Unpack
    def unpack(self, vtx_ren_flag):
        if vtx_ren_flag>>0 & 0x01 == 1:
            self.dlist0_0 = True
        if vtx_ren_flag>>1 & 0x01 == 1:
            self.dlist0_1 = True
        if vtx_ren_flag>>2 & 0x01 == 1:
            self.dlist1_0 = True
        if vtx_ren_flag>>3 & 0x01 == 1:
            self.dlist1_1 = True
        if vtx_ren_flag>>4 & 0x01 == 1:
            self.dlist2_0 = True
        if vtx_ren_flag>>5 & 0x01 == 1:
            self.dlist2_1 = True
        if vtx_ren_flag>>6 & 0x01 == 1:
            self.dlist3_0 = True
        if vtx_ren_flag>>7 & 0x01 == 1:
            self.dlist3_1 = True
    
    #Pack
    def pack(self):
        flags = 0x00
        if self.dlist0_0 == True:
            flags = flags + (0x01 << 0x00)
        if self.dlist0_1 == True:
            flags = flags + (0x01 << 0x01)
        if self.dlist1_0 == True:
            flags = flags + (0x01 << 0x02)
        if self.dlist1_1 == True:
            flags = flags + (0x01 << 0x03)
        if self.dlist2_0 == True:
            flags = flags + (0x01 << 0x04)
        if self.dlist2_1 == True:
            flags = flags + (0x01 << 0x05)
        if self.dlist3_0 == True:
            flags = flags + (0x01 << 0x06)
        if self.dlist3_1 == True:
            flags = flags + (0x01 << 0x07)
        return flags


class VertexAttribute:
    def __init__(self):
        self.gx_va_pnmtxidx = False
        self.gx_va_tex0mtxidx = False
        self.gx_va_tex1mtxidx = False
        self.gx_va_tex2mtxidx = False
        self.gx_va_tex3mtxidx = False
        self.gx_va_tex4mtxidx = False
        self.gx_va_tex5mtxidx = False
        self.gx_va_tex6mtxidx = False
        self.gx_va_tex7mtxidx = False
        self.gx_va_pos = False
        self.gx_va_nrm = False
        self.gx_va_clr0 = False
        self.gx_va_clr1 = False
        self.gx_va_tex0 = False
        self.gx_va_tex1 = False
        self.gx_va_tex2 = False
        self.gx_va_tex3 = False
        self.gx_va_tex4 = False
        self.gx_va_tex5 = False
        self.gx_va_tex6 = False
        self.gx_va_tex7 = False
        self.gx_va_pos_mtx_array = False
        self.gx_va_nrm_mtx_array = False
        self.gx_va_tex_mtx_array = False
        self.gx_va_light = False
        self.gx_va_nbt = False
    
    #Unpack
    def unpack(self, vertex_descriptor):
        if vertex_descriptor >> 0x00 & 0x01 == 0x01:
            self.gx_va_pnmtxidx = True
        if vertex_descriptor >> 0x01 & 0x01 == 0x01:
            self.gx_va_tex0mtxidx = True
        if vertex_descriptor >> 0x02 & 0x01 == 0x01:
            self.gx_va_tex1mtxidx = True
        if vertex_descriptor >> 0x03 & 0x01 == 0x01:
            self.gx_va_tex2mtxidx = True
        if vertex_descriptor >> 0x04 & 0x01 == 0x01:
            self.gx_va_tex3mtxidx = True
        if vertex_descriptor >> 0x05 & 0x01 == 0x01:
            self.gx_va_tex4mtxidx = True
        if vertex_descriptor >> 0x06 & 0x01 == 0x01:
            self.gx_va_tex5mtxidx = True
        if vertex_descriptor >> 0x07 & 0x01 == 0x01:
            self.gx_va_tex6mtxidx = True
        if vertex_descriptor >> 0x08 & 0x01 == 0x01:
            self.gx_va_tex7mtxidx = True
        if vertex_descriptor >> 0x09 & 0x01 == 0x01:
            self.gx_va_pos = True
        if vertex_descriptor >> 0x0A & 0x01 == 0x01:
            self.gx_va_nrm = True
        if vertex_descriptor >> 0x0B & 0x01 == 0x01:
            self.gx_va_clr0 = True
        if vertex_descriptor >> 0x0C & 0x01 == 0x01:
            self.gx_va_clr1 = True
        if vertex_descriptor >> 0x0D & 0x01 == 0x01:
            self.gx_va_tex0 = True
        if vertex_descriptor >> 0x0E & 0x01 == 0x01:
            self.gx_va_tex1 = True
        if vertex_descriptor >> 0x0F & 0x01 == 0x01:
            self.gx_va_tex2 = True
        if vertex_descriptor >> 0x10 & 0x01 == 0x01:
            self.gx_va_tex3 = True
        if vertex_descriptor >> 0x11 & 0x01 == 0x01:
            self.gx_va_tex4 = True
        if vertex_descriptor >> 0x12 & 0x01 == 0x01:
            self.gx_va_tex5 = True
        if vertex_descriptor >> 0x13 & 0x01 == 0x01:
            self.gx_va_tex6 = True
        if vertex_descriptor >> 0x14 & 0x01 == 0x01:
            self.gx_va_tex7 = True
        if vertex_descriptor >> 0x15 & 0x01 == 0x01:
            self.gx_va_pos_mtx_array = True
        if vertex_descriptor >> 0x16 & 0x01 == 0x01:
            self.gx_va_nrm_mtx_array = True
        if vertex_descriptor >> 0x17 & 0x01 == 0x01:
            self.gx_va_tex_mtx_array = True
        if vertex_descriptor >> 0x18 & 0x01 == 0x01:
            self.gx_va_light = True
        if vertex_descriptor >> 0x19 & 0x01 == 0x01:
            self.gx_va_nbt = True
    
    #Pack
    def pack(self):
        flags = 0x00
        if self.gx_va_pnmtxidx == True:
            flags = flags + (0x01 << 0x00)
        if self.gx_va_tex0mtxidx == True:
            flags = flags + (0x01 << 0x01)
        if self.gx_va_tex1mtxidx == True:
            flags = flags + (0x01 << 0x02)
        if self.gx_va_tex2mtxidx == True:
            flags = flags + (0x01 << 0x03)
        if self.gx_va_tex3mtxidx == True:
            flags = flags + (0x01 << 0x04)
        if self.gx_va_tex4mtxidx == True:
            flags = flags + (0x01 << 0x05)
        if self.gx_va_tex5mtxidx == True:
            flags = flags + (0x01 << 0x06)
        if self.gx_va_tex6mtxidx == True:
            flags = flags + (0x01 << 0x07)
        if self.gx_va_tex7mtxidx == True:
            flags = flags + (0x01 << 0x08)
        if self.gx_va_pos == True:
            flags = flags + (0x01 << 0x09)
        if self.gx_va_nrm == True:
            flags = flags + (0x01 << 0x0A)
        if self.gx_va_clr0 == True:
            flags = flags + (0x01 << 0x0B)
        if self.gx_va_clr1 == True:
            flags = flags + (0x01 << 0x0C)
        if self.gx_va_tex0 == True:
            flags = flags + (0x01 << 0x0D)
        if self.gx_va_tex1 == True:
            flags = flags + (0x01 << 0x0E)
        if self.gx_va_tex2 == True:
            flags = flags + (0x01 << 0x0F)
        if self.gx_va_tex3 == True:
            flags = flags + (0x01 << 0x10)
        if self.gx_va_tex4 == True:
            flags = flags + (0x01 << 0x11)
        if self.gx_va_tex5 == True:
            flags = flags + (0x01 << 0x12)
        if self.gx_va_tex6 == True:
            flags = flags + (0x01 << 0x13)
        if self.gx_va_tex7 == True:
            flags = flags + (0x01 << 0x14)
        if self.gx_va_pos_mtx_array == True:
            flags = flags + (0x01 << 0x15)
        if self.gx_va_nrm_mtx_array == True:
            flags = flags + (0x01 << 0x16)
        if self.gx_va_tex_mtx_array == True:
            flags = flags + (0x01 << 0x17)
        if self.gx_va_light == True:
            flags = flags + (0x01 << 0x18)
        if self.gx_va_nbt == True:
            flags = flags + (0x01 << 0x19)
        return flags
    

#GCMF Material
class Material:
    fmt = '1h16B1b3B3h1I'
    # 1h   16B                            
    # 0,   1, 2, 3-6, 7-10, 11-14, 15, 16,
    # 1b  3B          3h     1I
    # 17, 18, 19, 20, 21-23, 24
    
    def __init__(self):
        self.unk0x02 = 0x00
        self.unk0x03 = 0x00
        self.color0 = [0, 0, 0, 0]
        self.color1 = [0, 0, 0, 0]
        self.color2 = [0, 0, 0, 0]
        self.emission = 0x00
        self.transparency = 0x00
        self.material_count = 0x00
        #Vertex Render Flag
        self.vtx_render = VertexRenderFlag()
        self.unk0x14 = 0x00
        self.unk0x15 = 0x00
        self.texture_indexs = []
        #Vertex Descriptor Flag
        self.vtx_descriptor = VertexAttribute()
    
    def unpack(self, file, endian):
        bytes = file.read(struct.calcsize(self.fmt))
        buff = struct.unpack_from(endian + self.fmt, bytes, 0)
        
        #0
        self.unk0x02 = buff[1]
        self.unk0x03 = buff[2]
        self.color0 = [ buff[3]/0xFF, buff[4]/0xFF, buff[5]/0xFF, buff[6]/0xFF ]
        self.color1 = [ buff[7]/0xFF, buff[8]/0xFF, buff[9]/0xFF,  buff[10]/0xFF ]
        self.color2 = [ buff[11]/0xFF, buff[12]/0xFF, buff[13]/0xFF, buff[14]/0xFF ]
        self.emission = buff[15]
        self.transparency = buff[16]
        self.material_count = buff[17]
        vtx_render = buff[18]
        self.vtx_render.unpack(vtx_render) 
        self.unk0x14 = buff[19]
        self.unk0x15 = buff[20]
        for i in range(3):
            idx = buff[21+i]
            self.texture_indexs.append(idx)
        vtx_descriptor = buff[24]

        self.vtx_descriptor.unpack(vtx_descriptor)

    def pack(self, file, endian):
        vat = self.vtx_descriptor.pack()
        print( MSG_INFO_DATA_HEX.format('VAT', vat) )
        buff = struct.pack(endian + self.fmt, \
                    0, \
                    self.unk0x02, self.unk0x03, \
                    int(self.color0[0]*0xFF), int(self.color0[1]*0xFF), int(self.color0[2]*0xFF), int(self.color0[3]*0xFF), \
                    int(self.color1[0]*0xFF), int(self.color1[1]*0xFF), int(self.color1[2]*0xFF), int(self.color1[3]*0xFF), \
                    int(self.color2[0]*0xFF), int(self.color2[1]*0xFF), int(self.color2[2]*0xFF), int(self.color2[3]*0xFF), \
                    self.emission, self.transparency, \
                    self.material_count, \
                    self.vtx_render.pack(), self.unk0x14, self.unk0x15, \
                    self.texture_indexs[0], self.texture_indexs[1], self.texture_indexs[2], \
                    vat)
        file.write(buff)
        

#GCMF Attribute
class Attribute:
    def __init__(self):
        self.is_16bit = False
        self.is_unk0x01 = False #Not Exsit?
        self.is_stiching = False
        self.is_skin = False
        self.is_effective = False
        
    #Unpack
    def unpack(self, attr):
        if attr>>0 & 0x01 == 1:
            self.is_16bit = True
        if attr>>1 & 0x01 == 1:
            self.is_unk0x01 = True
        if attr>>2 & 0x01 == 1:
            self.is_stiching = True
        if attr>>3 & 0x01 == 1:
            self.is_skin = True
        if attr>>4 & 0x01 == 1:
            self.is_effective = True
    
    #Pack
    def pack(self):
        flags = 0x00
        if self.is_16bit == True:
            flags = flags + (0x01 << 0x00)
        if self.is_unk0x01 == True:
            flags = flags + (0x01 << 0x01)
        if self.is_stiching == True:
            flags = flags + (0x01 << 0x02)
        if self.is_skin == True:
            flags = flags + (0x01 << 0x03)
        if self.is_effective == True:
            flags = flags + (0x01 << 0x04)
        return flags


class Vertex:
    # 12f   4I
    # 0-11, 12, 13, 14, 15
    fmt_skin = '12f4I'
    # 12h   2B  3H
    # 0-11, 12, 13, 14, 15
    fmt_16bit_skin = '12h2B3H'
    fmt_idx = '1b'
    fmt_vtx = '{0}f'
    fmt_vtx_16 = '{0}h'
    fmt_clr = '1I'
    #FiXed-int coefficient
    fx = 8191.0
    
    def __init__(self):
        self.offs = 0x00
        self.pnmtxidx = -1
        self.tex0mtxidx = -1
        self.tex1mtxidx = -1
        self.tex2mtxidx = -1
        self.tex3mtxidx = -1
        self.tex4mtxidx = -1
        self.tex5mtxidx = -1
        self.tex6mtxidx = -1
        self.tex7mtxidx = -1
        self.pos = [0.0, 0.0, 0.0]
        self.nrm = [0.0, 0.0, 0.0]
        self.clr0 = [1.0, 1.0, 1.0, 1.0]
        self.clr1 = [1.0, 1.0, 1.0, 1.0]
        self.tex0 = [0.0, 0.0]
        self.tex1 = [0.0, 0.0]
        self.tex2 = [0.0, 0.0]
        self.tex3 = [0.0, 0.0]
        self.tex4 = [0.0, 0.0]
        self.tex5 = [0.0, 0.0]
        self.tex6 = [0.0, 0.0]
        self.tex7 = [0.0, 0.0]
        self.pos_mtx_array = []
        self.nrm_mtx_array = []
        self.tex_mtx_array = []
        self.light = [0.0, 0.0, 0.0]
        self.nbt = [ [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0] ]
        # unknown
        self.unk_0x34 = 0x00
        self.unk_0x38 = 0x00
        self.unk_0x3C = 0x00
    
    #Unpack Index
    def unpack_idx(self, file, endian):
        bytes = file.read(struct.calcsize(self.fmt_idx))
        buff = struct.unpack_from(endian + self.fmt_idx, bytes, 0)
        idx = buff[0]
        return idx
    
    #Pack Index
    def pack_idx(self, file, endian, idx):
        buff = struct.pack(endian + self.fmt_idx, idx[0])
        file.write(buff)
    
    #Unpack Color
    def unpack_clr(self, file, endian):
        fmt = self.fmt_clr
        bytes = file.read(struct.calcsize(fmt))
        buff = struct.unpack_from(endian + fmt, bytes, 0)
        r = ((buff[0] >> 0x18) & 0xFF)/0xFF
        g = ((buff[0] >> 0x10) & 0xFF)/0xFF
        b = ((buff[0] >> 0x08) & 0xFF)/0xFF
        a = ((buff[0] >> 0x00) & 0xFF)/0xFF
        clr = [ r, g, b, a ]
        return clr
    
    #Pack Color
    def pack_clr(self, file, endian, clr):
        r = int(clr[0]*0xFF)
        g = int(clr[1]*0xFF)
        b = int(clr[2]*0xFF)
        a = int(clr[3]*0xFF)
        bin_clr = 0x00
        bin_clr = bin_clr + (r << 0x18)
        bin_clr = bin_clr + (g << 0x10)
        bin_clr = bin_clr + (b << 0x08)
        bin_clr = bin_clr + (a << 0x00)
        buff = struct.pack(endian + self.fmt_clr, bin_clr)
        file.write(buff)
    
    #Unpack Vector3
    def unpack_vec3(self, file, endian, is_16bit):
        fmt = (self.fmt_vtx_16 if is_16bit else self.fmt_vtx).format(3)
        bytes = file.read(struct.calcsize(fmt))
        buff = struct.unpack_from(endian + fmt, bytes, 0)
        if (is_16bit):
            vec3 = [ buff[0]/self.fx, buff[1]/self.fx, buff[2]/self.fx ]
        else:
            vec3 = [ buff[0], buff[1], buff[2] ]
        return vec3
    
    #Pack Vector3
    def pack_vec3(self, file, endian, is_16bit, vec3):
        fmt = (self.fmt_vtx_16 if is_16bit else self.fmt_vtx).format(3)
        if (is_16bit):
            x = int(vec3[0]*self.fx)
            y = int(vec3[1]*self.fx)
            z = int(vec3[2]*self.fx)
            buff = struct.pack(endian + fmt, x, y, z)
        else:
            buff = struct.pack(endian + fmt, vec3[0], vec3[1], vec3[2])
        file.write(buff)
    
    #Unpack Vector2
    def unpack_vec2(self, file, endian, is_16bit):
        fmt = (self.fmt_vtx_16 if is_16bit else self.fmt_vtx).format(2)
        bytes = file.read(struct.calcsize(fmt))
        buff = struct.unpack_from(endian + fmt, bytes, 0)
        if (is_16bit):
            vec2 = [ buff[0]/self.fx, buff[1]/self.fx ]
        else:
            vec2 = [ buff[0], buff[1] ]
        return vec2
    
    #Pack Vector2
    def pack_vec2(self, file, endian, is_16bit, vec2):
        fmt = (self.fmt_vtx_16 if is_16bit else self.fmt_vtx).format(2)
        if (is_16bit):
            u = int(vec2[0]*self.fx)
            v = int(vec2[1]*self.fx)
            buff = struct.pack(endian + fmt, u, v)
        else:
            buff = struct.pack(endian + fmt, vec2[0], vec2[1])
        file.write(buff)
    
    #Unpack Unknowns
    def unpack_unk(self, file, endian, is_16bit):
        fmt = (self.fmt_vtx_16 if is_16bit else self.fmt_vtx).format(1)
        bytes = file.read(struct.calcsize(fmt))
        buff = struct.unpack_from(endian + fmt, bytes, 0)
        if (is_16bit):
            val = buff[0]/self.fx
        else:
            val = buff[0]
        return val
    
    def unpack(self, file, endian, attribute, vertex_attribute, base_offs = 0x00):
        print( MSG_INFO_DATA_HEX.format('Vertex Address', file.tell()) )
        if (attribute.is_skin or attribute.is_effective):

            self.pos = self.unpack_vec3(file, endian, attribute.is_16bit)
            self.nrm = self.unpack_vec3(file, endian, attribute.is_16bit)
            self.tex0 = self.unpack_vec2(file, endian, attribute.is_16bit)
            self.tex1 = self.unpack_vec2(file, endian, attribute.is_16bit)
            self.tex2 = self.unpack_vec2(file, endian, attribute.is_16bit)
            self.clr0 = self.unpack_clr(file, endian)
            #Unknown7_1 , Unknown7_2, Unknown7_3
            self.unk_0x34 = self.unpack_unk(file, endian, attribute.is_16bit)
            
            #Maybe these are padding?
            self.unk_0x38 = self.unpack_unk(file, endian, attribute.is_16bit)
            if(attribute.is_16bit == False):
                self.unk_0x3C = self.unpack_unk(file, endian, attribute.is_16bit)
        else:
            #default, 16bit, stiching
            self.offs = file.tell()
        
            if vertex_attribute.gx_va_pnmtxidx == True:
                self.pnmtxidx = self.unpack_idx(file, endian)
            if vertex_attribute.gx_va_tex0mtxidx == True:
                self.tex0mtxidx = self.unpack_idx(file, endian)
            if vertex_attribute.gx_va_tex1mtxidx == True:
                self.tex1mtxidx = self.unpack_idx(file, endian)
            if vertex_attribute.gx_va_tex2mtxidx == True:
                self.tex2mtxidx = self.unpack_idx(file, endian)
            if vertex_attribute.gx_va_tex3mtxidx == True:
                self.tex3mtxidx = self.unpack_idx(file, endian)
            if vertex_attribute.gx_va_tex4mtxidx == True:
                self.tex4mtxidx = self.unpack_idx(file, endian)
            if vertex_attribute.gx_va_tex5mtxidx == True:
                self.tex5mtxidx = self.unpack_idx(file, endian)
            if vertex_attribute.gx_va_tex6mtxidx == True:
                self.tex6mtxidx = self.unpack_idx(file, endian)
            if vertex_attribute.gx_va_tex7mtxidx == True:
                self.tex7mtxidx = self.unpack_idx(file, endian)
            if vertex_attribute.gx_va_pos == True:
                self.pos = self.unpack_vec3(file, endian, attribute.is_16bit)
            if vertex_attribute.gx_va_nrm == True:
                self.nrm = self.unpack_vec3(file, endian, attribute.is_16bit)
            if vertex_attribute.gx_va_nbt == True:
                print('nbt :  {0:#X}'.format(file.tell()))
                fmt = (self.fmt_vtx_16 if attribute.is_16bit else self.fmt_vtx).format(9)
                bytes = file.read(struct.calcsize(fmt))
                buff = struct.unpack_from(endian + fmt, bytes, 0)
                self.nrm = [ buff[0], buff[1], buff[2] ]
                self.nbt[1] = [ buff[3], buff[4], buff[5] ]
                self.nbt[2] = [ buff[6], buff[7], buff[8] ]
            if vertex_attribute.gx_va_clr0 == True:
                self.clr0 = self.unpack_clr(file, endian)
            if vertex_attribute.gx_va_clr1 == True:
                self.clr1 = self.unpack_clr(file, endian)
            if vertex_attribute.gx_va_tex0 == True:
                self.tex0 = self.unpack_vec2(file, endian, attribute.is_16bit)
            if vertex_attribute.gx_va_tex1 == True:
                self.tex1 = self.unpack_vec2(file, endian, attribute.is_16bit)
            if vertex_attribute.gx_va_tex2 == True:
                self.tex2 = self.unpack_vec2(file, endian, attribute.is_16bit)
            if vertex_attribute.gx_va_tex3 == True:
                self.tex3 = self.unpack_vec2(file, endian, attribute.is_16bit)
            if vertex_attribute.gx_va_tex4 == True:
                self.tex4 = self.unpack_vec2(file, endian, attribute.is_16bit)
            if vertex_attribute.gx_va_tex5 == True:
                self.tex5 = self.unpack_vec2(file, endian, attribute.is_16bit)
            if vertex_attribute.gx_va_tex6 == True:
                self.tex6 = self.unpack_vec2(file, endian, attribute.is_16bit)
            if vertex_attribute.gx_va_tex7 == True:
                self.tex7 = self.unpack_vec2(file, endian, attribute.is_16bit)
            #if vertex_attribute.gx_va_pos_mtx_array == True:
            #    self.pos_mtx_array = mtx
            #if vertex_attribute.gx_va_nrm_mtx_array == True:
            #    self.nrm_mtx_array = mtx
            #if vertex_attribute.gx_va_tex_mtx_array == True:
            #    self.tex_mtx_array = mtx
            if vertex_attribute.gx_va_light == True:
                self.light = self.unpack_vec3(file, endian, attribute.is_16bit)

    def pack(self, file, endian, attribute, vertex_attribute):
        print( MSG_INFO_DATA_HEX.format('Vertex Address', file.tell()) )
        if (attribute.is_skin or attribute.is_effective):
            #skin, effective
            buff = struct.pack(endian + self.fmt_skin, \
                self.pos[0], self.pos[1], self.pos[2], \
                self.nrm[0], self.nrm[1], self.nrm[2], \
                self.tex0[0], self.tex0[1], \
                self.tex1[0], self.tex1[1], \
                self.clr0[0], self.clr0[1], self.clr0[2], self.clr0[3], \
                self.unk_0x34, self.unk_0x38, self.unk_0x3C)
        else:
            #default, 16bit, stiching
            if vertex_attribute.gx_va_pnmtxidx == True:
                self.pack_idx(file, endian, self.pnmtxidx)
            if vertex_attribute.gx_va_tex0mtxidx == True:
                self.pack_idx(file, endian, self.tex0mtxidx)
            if vertex_attribute.gx_va_tex1mtxidx == True:
                self.pack_idx(file, endian, self.tex1mtxidx)
            if vertex_attribute.gx_va_tex2mtxidx == True:
                self.pack_idx(file, endian, self.tex2mtxidx)
            if vertex_attribute.gx_va_tex3mtxidx == True:
                self.pack_idx(file, endian, self.tex3mtxidx)
            if vertex_attribute.gx_va_tex4mtxidx == True:
                self.pack_idx(file, endian, self.tex4mtxidx)
            if vertex_attribute.gx_va_tex5mtxidx == True:
                self.pack_idx(file, endian, self.tex5mtxidx)
            if vertex_attribute.gx_va_tex6mtxidx == True:
                self.pack_idx(file, endian, self.tex6mtxidx)
            if vertex_attribute.gx_va_tex7mtxidx == True:
                self.pack_idx(file, endian, self.tex7mtxidx)
            if vertex_attribute.gx_va_pos == True:
                self.pack_vec3(file, endian, attribute.is_16bit, self.pos)
            if vertex_attribute.gx_va_nrm == True:
                self.pack_vec3(file, endian, attribute.is_16bit, self.nrm)
            if vertex_attribute.gx_va_clr0 == True:
                self.pack_clr(file, endian, self.clr0)
            if vertex_attribute.gx_va_clr1 == True:
                self.pack_clr(file, endian, self.clr1)
            if vertex_attribute.gx_va_tex0 == True:
                self.pack_vec2(file, endian, attribute.is_16bit, self.tex0)
            if vertex_attribute.gx_va_tex1 == True:
                self.pack_vec2(file, endian, attribute.is_16bit, self.tex1)
            if vertex_attribute.gx_va_tex2 == True:
                self.pack_vec2(file, endian, attribute.is_16bit, self.tex2)
            if vertex_attribute.gx_va_tex3 == True:
                self.pack_vec2(file, endian, attribute.is_16bit, self.tex3)
            if vertex_attribute.gx_va_tex4 == True:
                self.pack_vec2(file, endian, attribute.is_16bit, self.tex4)
            if vertex_attribute.gx_va_tex5 == True:
                self.pack_vec2(file, endian, attribute.is_16bit, self.tex5)
            if vertex_attribute.gx_va_tex6 == True:
                self.pack_vec2(file, endian, attribute.is_16bit, self.tex6)
            if vertex_attribute.gx_va_tex7 == True:
                self.pack_vec2(file, endian, attribute.is_16bit, self.tex7)
            #if vertex_attribute.gx_va_pos_mtx_array == True:
            #    self.pos_mtx_array = mtx
            #if vertex_attribute.gx_va_nrm_mtx_array == True:
            #    self.nrm_mtx_array = mtx
            #if vertex_attribute.gx_va_tex_mtx_array == True:
            #    self.tex_mtx_array = mtx
            if vertex_attribute.gx_va_light == True:
                self.pack_vec3(file, endian, attribute.is_16bit, self.light)
            if vertex_attribute.gx_va_nbt == True:
                fmt = (self.fmt_vtx_16 if attribute.is_16bit else self.fmt_vtx).format(9)
                buff = struct.pack(endian + fmt, \
                    self.nbt[0][0], self.nbt[0][1], self.nbt[0][2], \
                    self.nbt[1][0], self.nbt[1][1], self.nbt[1][2], \
                    self.nbt[2][0], self.nbt[2][1], self.nbt[2][2], \
                    )
                file.write(buff)

class Strip:
    fmt = '1B1H'            #default,  #16bit, stiching
    fmt_skin_16bit = '{0}H'   #skin(16bit), effective(16bit)
    fmt_skin = '{0}I'         #skin, effective
    
    def __init__(self):
        self.cmd = 0x00
        self.count = 0x00
        self.vertexs = []
    
    def unpack(self, file, endian, attribute, vertex_attribute, vertex_controll):
        if (attribute.is_skin or attribute.is_effective):
            #skin, effective
            type = self.fmt_skin_16bit if attribute.is_16bit else self.fmt_skin
            size = type.format(1)
            bytes = file.read(struct.calcsize(size))
            buff = struct.unpack_from(endian + size, bytes, 0)
            self.count = buff[0]

            #get vertex offsets
            size = type.format(self.count)
            bytes = file.read(struct.calcsize(size))
            vtx_offss = struct.unpack_from(endian + size, bytes, 0)

            offs = 0x00
            for vtx_offs in vtx_offss:
                #store current VertexControll's offset3 section
                offs = file.tell()
                #seek vertex offset + VertexControll's offset_2 + VertexControll's base offset
                file.seek(vtx_offs + vertex_controll.offset_2 + vertex_controll.base_offs)
                vertex = Vertex()
                vertex.unpack(file, endian, attribute, vertex_attribute, vertex_controll.base_offs)
                self.vertexs.append(vertex)
                #seek VertexControll's offset3 section
                file.seek(offs)
        else:
            #default, 16bit, stiching
            bytes = file.read(3)
            buff = struct.unpack_from(endian + self.fmt, bytes, 0)
            self.cmd = buff[0]
            self.count = buff[1]
            for i in range(self.count):
                vertex = Vertex()
                vertex.unpack(file, endian, attribute, vertex_attribute)
                self.vertexs.append(vertex)

    def pack(self, file, endian, attribute, vertex_attribute):
        if (attribute.is_skin or attribute.is_effective):
            #skin, effective
            #TODO: implement this
            buff = struct.pack(endian + self.fmt_skin, \
                self.count)
        else:
            #default, 16bit, stiching
            buff = struct.pack(endian + self.fmt, \
                self.cmd, self.count)
        file.write(buff)
        for vertex in self.vertexs:
            vertex.pack(file, endian, attribute, vertex_attribute)
                        
class DisplayList:
    def __init__(self):
        self.strips = []
    
    def unpack(self, file, endian, attribute, vtx_attribute, dlist_end_offs, vertex_controll):
        print( MSG_INFO_DATA_HEX.format('DisplayList End Addres: {0:#X}', dlist_end_offs) )
        
        #seek 1byte for 16bit, stiching
        file.seek(file.tell() + 0x01)
        if (attribute.is_skin or attribute.is_effective):
            #skin and effective needs ignore "+1 seek"
            file.seek(file.tell() - 0x01)
        while file.tell() < dlist_end_offs - 0x03:
            strip = Strip()
            strip.unpack(file, endian, attribute, vtx_attribute, vertex_controll)
            if (strip.count == 0x00):
                break
            self.strips.append(strip)
        file.seek(dlist_end_offs)

    def pack(self, file, endian, attribute, vtx_attribute):
		#seek 1byte for 16bit, stiching
        file.write(bytes(1))
        if (attribute.is_skin or attribute.is_effective):
            #skin and effective needs ignore "+1 seek"
            file.seek(file.tell() - 0x01)
        for strip in self.strips:
            strip.pack(file, endian, attribute, vtx_attribute)
        #Padding
        while (file.tell() % 0x20 != 0x00):
            file.write(bytes(1))
        

class DisplatListHeader:
    fmt = '8b2i'
    # 8b   2i
    # 0-7, 8-9
    
    def __init__(self):
        self.submesh_end_offs = 0x00
        self.trans_mtxs = []
        self.dlist_sizes = []
        
    def unpack(self, file, endian):
        bytes = file.read(struct.calcsize(self.fmt))
        buff = struct.unpack_from(endian + self.fmt, bytes, 0)
        
        for i in range(8):
            idx = buff[i]
            self.trans_mtxs.append(idx)
        sizes = []
        for i in range(2):
            size = buff[8+i]
            self.dlist_sizes.append(size)
    
    def pack(self, file, endian):
        buff = struct.pack(endian + self.fmt, \
                self.trans_mtxs[0], self.trans_mtxs[1], self.trans_mtxs[2], self.trans_mtxs[3], \
                self.trans_mtxs[4], self.trans_mtxs[5], self.trans_mtxs[6], self.trans_mtxs[7], \
                self.dlist_sizes[0], self.dlist_sizes[1])
        file.write(buff)
        
        
#GCMF Submesh
class Submesh:
    fmt = '4f1I28x'
    # 4f      1I  28x
    # 0-2, 3, 4
    
    def __init__(self):
        self.material = Material()
        self.dlist_headers = []
        self.boundingsphere_origin = [0.0, 0.0, 0.0]
        self.unk0x3C = 0x00
        self.unk0x40 = 0x00
        self.dlists = []
    
    def unpack(self, file, endian, attribute, vertex_controll, vtxcon_offs3):
        print( MSG_INFO_DATA_HEX.format('Submesh Offset', file.tell()) )
        self.material.unpack(file, endian)
        
        dlist_header = DisplatListHeader()
        dlist_header.unpack(file, endian)

        bytes = file.read(struct.calcsize(self.fmt))
        buff = struct.unpack_from(endian + self.fmt, bytes, 0)
                    
        self.boundingsphere_origin = [buff[0], buff[1], buff[2]]
        self.unk0x3C = buff[3]
        self.unk0x40 = buff[4]
        
        dlist_header.submesh_end_offs = file.tell()
        self.dlist_headers.append(dlist_header)

        #DisplayListFlag
        vtx_render = self.material.vtx_render
        
        #ExtraDisplayListHeader
        if(vtx_render.dlist1_0 or vtx_render.dlist1_1):
            #dlist_1_0 or dlist_1_1 Exist
            print('Detect ExtraDisplayList')
            offs = 0x00
            for dlist_size in self.dlist_headers[0].dlist_sizes:
                offs = offs + dlist_size
            #Seek to ExtraDisplayListHeader
            file.seek(file.tell() + offs)
            print( MSG_INFO_DATA_HEX.format('Seek(Extra DisplayList Load)', file.tell()) )
            #Store submesh offset
            dlist_header = DisplatListHeader()
            dlist_header.unpack(file, endian)
            file.seek(file.tell() + 0x10)
            dlist_header.submesh_end_offs = file.tell()
            self.dlist_headers.append(dlist_header)
        
        #Read DisplayList
        vtx_attribute = self.material.vtx_descriptor
        for dlist_header in self.dlist_headers:
            dlist_end_offs = 0x00
            dlist_offs = 0x00
            if (attribute.is_skin or attribute.is_effective):
                #skin, effective
                dlist_offs = vertex_controll.base_offs + vtxcon_offs3
                print( MSG_INFO_DATA_HEX.format('Submesh VertexControll Offset 3', dlist_offs) )
            else:
                #16bit, stiching
                dlist_offs = dlist_header.submesh_end_offs
            dlist_end_offs = dlist_offs
            print( MSG_INFO_DATA_HEX.format('Submesh End Offset', dlist_end_offs) )
            #seek to VertexControll's offset 3 or Submesh End Offset
            file.seek(dlist_offs)
            for i, dlist_size in enumerate(dlist_header.dlist_sizes):
                if (attribute.is_skin or attribute.is_effective):
                    #skin, effective
                    #needs to dlist_size * 0x04
                    print('DisplayList{0} Length: {1:#X}'.format(i, dlist_size))
                    print('DisplayList{0} Size: {1:#X}'.format(i, dlist_size * 0x04))
                    dlist_end_offs = dlist_end_offs + (dlist_size * 0x04)
                else:
                    #default, 16bit, stiching
                    print('DisplayList{0} Size: {1:#X}'.format(i, dlist_size))
                    dlist_end_offs = dlist_end_offs + dlist_size
                #read displaylist
                if file.tell() <= dlist_end_offs:
                    dlist = DisplayList()
                    dlist.unpack(file, endian, attribute, vtx_attribute, dlist_end_offs, vertex_controll)
                    self.dlists.append(dlist)
        #seek to submesh offset(Back)
        if (attribute.is_skin or attribute.is_effective):
            #skin, effective needs
            file.seek(dlist_header.submesh_end_offs)

    def pack(self, file, endian, attribute):
        self.material.pack(file, endian)
        
        for dlist_header in self.dlist_headers:
            #initialize DisplayList Size
            dlist_sizes = [0x00, 0x00]
            
            #Store DisplayList Header Offset
            offs_dlist_header = file.tell()
            #Skip DisplayList Header
            file.seek(offs_dlist_header + 0x10)
            #Write
            buff = struct.pack(endian + self.fmt, \
                    self.boundingsphere_origin[0], self.boundingsphere_origin[1], self.boundingsphere_origin[2], \
                    self.unk0x3C, self.unk0x40)
            file.write(buff)
            
            vtx_attribute = self.material.vtx_descriptor
            for i, dlist in enumerate(self.dlists):
                offs_dlist_start = file.tell()
                dlist.pack(file, endian, attribute, vtx_attribute)
                offs_dlist_end = file.tell()
                size = offs_dlist_end - offs_dlist_start
                dlist_sizes[i] = size
            
            dlist_header.dlist_sizes = dlist_sizes
            #Store End Postion
            offs = file.tell()
            #Go To DisplayList Header Offset
            file.seek( offs_dlist_header )
            #Write DisplayList Header
            dlist_header.pack(file, endian)
            #Go Back End Postion
            file.seek(offs)


#GCMF
class Gcmf():
    magic = 'GCMF'
    fmt = '4s1I4f3h2b2i8b16x'
    # 4s 1I 4f   3h   2b    2I     8b     16x
    # 0, 1, 2-5, 6-8, 9-10, 11-12, 13-20
    
    def __init__(self):
        self.name = ''
        self.attribute = Attribute()
        self.origin = [0.0, 0.0, 0.0]
        self.boundspher_radius = 1.0
        self.texture_count = 0
        self.opaque_count = 0
        self.transparent_count = 0
        self.mtx_count = 0
        self.submesh_offset = 0
        #
        self.mtx_idxs = []
        self.textures = []
        self.mtxs = []
        self.vertex_controll = VertexControll()
        self.submeshs = []
        
    #Unpack
    def unpack(self, file, endian):
        print('-------------------')
        gcmf_offset = file.tell()
        
        bytes = file.read(struct.calcsize(self.fmt))
        buff = struct.unpack_from(endian + self.fmt, bytes, 0)

        magic_str = buff[0].decode(CHAR_SET)

        # check GCMF Magic
        if (magic_str[::-1] if endian == '<' else magic_str) != self.magic:
            print(MSG_WARN_NOT_GCMF.format(magic_str, self.magic))
        else:
            attr = buff[1]
            self.attribute.unpack(attr)
            self.origin = [buff[2], buff[3], buff[4]]
            self.boundspher_radius = buff[5]
            self.texture_count = buff[6]
            self.opaque_count = buff[7]
            self.transparent_count = buff[8]
            self.mtx_count = buff[9]
            # buff[10]
            self.submesh_offset = buff[11]
            # buff[12]
            for i in range(8):
                idx = buff[13+i]
                self.mtx_idxs.append(idx)

            #Gcmf Texture
            for i in range(self.texture_count):
                texture = Texture()
                texture.unpack(file, endian)
                self.textures.append(texture)
            
            #GCMF Transform Matrix
            for i in range(self.mtx_count):
                mtx = TransformMatrix()
                mtx.unpack(file, endian)
                self.mtxs.append(mtx)
            if file.tell()%0x20 != 0x00:
                file.seek(file.tell() + 0x10)

            #isMatrix = (self.attribute.is_skin or self.attribute.is_effective)
            #print('Contains Transoform Matrix: {0}'.format(isMatrix))
            #if isMatrix :
            #    for i in range(self.mtx_count):
            #        mtx = TransformMatrix()
            #        mtx.read(file, endian)
            #        self.mtxs.append(mtx)
            #    if file.tell()%0x20 != 0x00:
            #        file.seek(file.tell() + 0x10)

            vtxcon_offs3 = 0x00
            submesh_offs = gcmf_offset + self.submesh_offset
            
            #GCMF VertexControll
            if(self.attribute.is_skin or self.attribute.is_effective):
                self.vertex_controll.unpack(file, endian)
                vtxcon_offs3 = self.vertex_controll.offset_3
                submesh_offs = submesh_offs + 0x20

            #GCMF Submesh
            file.seek(submesh_offs)
            submesh_count = self.opaque_count + self.transparent_count
            print( MSG_INFO_DATA.format('Mesh Count', submesh_count) )
            for i in range(submesh_count):
                submesh = Submesh()
                submesh.unpack(file, endian, self.attribute, self.vertex_controll, vtxcon_offs3)
                if(self.attribute.is_skin or self.attribute.is_effective):
                    #move vtxcon_offs3 section's offset
                    dlist_offs = 0x00
                    for dlist_header in submesh.dlist_headers:
                        for dlist_size in dlist_header.dlist_sizes:
                            dlist_offs = dlist_offs + dlist_size
                    dlist_offs = dlist_offs * 0x4
                    vtxcon_offs3 = vtxcon_offs3 + dlist_offs
                self.submeshs.append(submesh)
                

    #Pack
    def pack(self, file, endian):
        print('----Pack----')
        print( MSG_INFO_DATA_HEX.format('GCMF Address', file.tell()) )
        # skip Gcmf Header
        gcmf_offset = file.tell()
        file.seek(gcmf_offset + struct.calcsize(self.fmt))
                    
        # Textures
        for texture in self.textures:
            texture.pack(file, endian)
        
        # Matrix
        for mtx in self.mtxs:
            mtx.pack(file, endian)
        
        # store Submesh offset
        submesh_offset = file.tell()
        self.submesh_offset = submesh_offset - gcmf_offset
        
        # Submesh
        for submesh in self.submeshs:
            submesh.pack(file, endian, self.attribute)

        #Store Gcmf End Offset
        end_offset = file.tell()
        #Go back Gcmf Header
        file.seek(gcmf_offset)
        #Write Gcmf Header
        magic = self.magic[::-1] if endian == '<' else self.magic
        gcmf_magic = bytes(magic.encode(CHAR_SET))
        buff = struct.pack(endian + self.fmt, \
                            gcmf_magic, self.attribute.pack(), \
                            self.origin[0], self.origin[1], self.origin[2], self.boundspher_radius, \
                            self.texture_count, self.opaque_count, self.transparent_count, \
                            self.mtx_count, 0, \
                            self.submesh_offset, 0, \
                            self.mtx_idxs[0], self.mtx_idxs[1], \
                            self.mtx_idxs[2], self.mtx_idxs[3], \
                            self.mtx_idxs[4], self.mtx_idxs[5], \
                            self.mtx_idxs[6], self.mtx_idxs[7])
        file.write(buff)
        file.seek(end_offset)