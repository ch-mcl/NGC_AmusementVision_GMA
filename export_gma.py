import bmesh
import bpy
import math
import mathutils
import struct

from .gma import Gma, GcmfEntry
from .gcmf import Gcmf, Attribute, \
Texture_Flags0x00, Texture_Mipmap, Texture_Wrap, Texture, TransformMatrix, \
Submesh, Material, \
VertexAttribute, VertexRenderFlag, DisplatListHeader, \
DisplayList, Vertex, Strip

#Messages
MSG_INFO_INIT = '---- {0} ----'
MSG_INFO_DATA = '{0}: {1}'
MSG_WARN_NONE_UV = 'Detect UV not exsit. exported any UV is (0.0, 0.0)'
MSG_WARN_MANY = 'Detect greater than {0} {1}s ({2}). Maybe this GCMF not works correct in Amusement Vision Games.'
MSG_WARN_TOO_MANY = 'Detect too many {0}s ({1}). Ignored {0}[{2}] and mores.'
MSG_WARN_NONE_MAT = 'Detect none Material Object. "{0}" is ignored. Mesh without Material Export is not support.'
MSG_WARN_FLAG_NONE = 'Detect {0}. But Check-Box is not checked. {1}'

#Generate UV-Wrap
#GMA    : Blender
#CLAMP  : EXTEND
#REPEAT : REPEAT
#MIRROR : REPEAT and MIRROR
#Blender can't set x and y repeat falgs unique
def generate_uvwrap(tex):
    uv_wrap = Texture_Wrap()

    extension = tex.extension
    if extension == 'REPEAT':
        uv_wrap.repeat_x = True
        uv_wrap.mirror_x = False
        uv_wrap.repeat_y = True
        uv_wrap.mirror_y = False
    
    if tex.use_mirror_x:
        uv_wrap.repeat_x = False
        uv_wrap.mirror_x = True
    if tex.use_mirror_y:
        uv_wrap.repeat_y = False
        uv_wrap.mirror_y = True
    
    return uv_wrap

#Generate Mipmap
def generate_mipmap(tex):
    mipmap = Texture_Mipmap()
    
    mipmap.enable = True
    mipmap.unknown1 = True
    mipmap.unknown2 = True
    
    return mipmap

#Generate Texture
def generate_texture(bl_tex, img_names, idx):
    #TODO: Convert from Blender's Texture
    print('-Texture')
    texture = Texture()
    
    tex = bpy.data.textures[bl_tex.name]
    image = tex.image
    
    #Texture flag
    unk0x00 = Texture_Flags0x00()
    #Mipmap
    texture.mipmap = generate_mipmap(tex)
    #UV wrap
    texture.uv_wrap = generate_uvwrap(tex)
    #Image Index
    img_idx = 0
    if image != None:
        img_name = image.name
        print(img_name)
        if 'tpl' in img_name:
            if 'common' in img_name:
                #Set commontex flag
                unk0x00.commontex = True
            
            #set index force
            split = img_name.split('.')
            img_name = split[0]
            img_idx = int(img_name[-3::])
        else:
            img_idx = img_names.index(img_name)
    print(MSG_INFO_DATA.format('Image Index', img_idx))
    texture.texture_index = img_idx
    
#    texture.unk0x06 = 2
#    texture.anisotropy = 0
#    texture.unk0x0C = 5
#    texture.is_swappable = True
    #themself index
    texture.index = idx
    
    coordinate = bl_tex.texture_coords
    if coordinate == 'NORMAL':
        unk0x00.unknown4 = True
    
    clr_strength = int(bl_tex.diffuse_color_factor * 0xFF)
    texture.unk0x0C = clr_strength
    
    texture.unk0x00 = unk0x00
    #TEV?
    texture.unk0x10 = 0x30
    if bl_tex.use_map_alpha == True:
        texture.unk0x10 = 0x00
    
    return texture

#TransformMatrix
def generate_matrix():
    matrix = TransformMatrix()
    mtx = mathutils.Matrix()
    
    #TODO: Convert from Blender's ...?
    #Node or Armature ???
    mtx[0][0] = 1
    mtx[0][1] = 2
    mtx[0][2] = 3
    mtx[0][3] = 4
    
    mtx[1][0] = 5
    mtx[1][1] = 6
    mtx[1][2] = 7
    mtx[1][3] = 8
    
    mtx[2][0] = 9
    mtx[2][1] = 10
    mtx[2][2] = 11
    mtx[2][3] = 12
    
    matrix.mtx = mtx
    return matrix

#Generate VAT
def generate_vat(bl_mat, bm):
    vat = VertexAttribute()
    
    #Position
    vat.gx_va_pos = True
    #Normal
    vat.gx_va_nrm = True
    
    #Color
    clr_count = len(bm.loops.layers.color)
    if bl_mat.material.use_vertex_color_paint == True:
        #Enable Vertex-Color
        if clr_count != 0:
            if clr_count > 0:
                vat.gx_va_clr0 = True
            if clr_count > 1:
                print(MSG_WARN_MANY.format(1, 'VERTEX-COLOR', clr_count))
                vat.gx_va_clr1 = True
            if clr_count > 2:
                 print(MSG_WARN_TOO_MANY.format('VERTEX-COLOR', clr_count, 2))
    #TEX0~7
    vat.gx_va_tex0 = True # force export UV0
    tex_slot = list(filter(None, bl_mat.material.texture_slots)) # removes None
    uv_count = len(tex_slot)
    if uv_count == 0:
        #UV is not exsit
        print(MSG_WARN_NONE_UV)
    else:
        if uv_count > 1:
            vat.gx_va_tex1 = True
        if uv_count > 2:
            vat.gx_va_tex2 = True
        if uv_count > 3:
            print(MSG_WARN_MANY.format(3, 'UV', uv_count))
            vat.gx_va_tex3 = True
        if uv_count > 4:
            vat.gx_va_tex4 = True
        if uv_count > 5:
            vat.gx_va_tex5 = True
        if uv_count > 6:
            vat.gx_va_tex6 = True
        if uv_count > 7:
            vat.gx_va_tex7 = True
        if uv_count > 8:
            print(MSG_WARN_TOO_MANY.format('UV', uv_count, 7))
        
    return vat

#Generate Material
#TODO: Convert from Blender Material
#TODO: something ways to restore import GMA values
def generate_matrial(bm, bl_mat, bl_tex_slots, tex_idx):
    print('-Material')
    material = Material()
    
    vtx_attr = generate_vat(bl_mat, bm)
    
    vtx_render = VertexRenderFlag()
    vtx_render.dlist0_0 = True

    texture_indexs = [-1, -1, -1]
    tex_count = 0

    tex_slots_count = len(bl_tex_slots)
    if tex_slots_count > 3:
        print(MSG_WARN_TOO_MANY.format('TEXTURE', tex_slots_count, 3))
    if (tex_slots_count > 0):
        for i in range( 3 if tex_slots_count > 2 else tex_slots_count ):
            # over MAX of UV layers
            texture_indexs[i] = tex_idx + i
        tex_count = i + 1

#    material.unk0x02 = 0x11
#    material.unk0x03 = 0x22
#    
#    material.emission = 0xFF
#    material.transparency = 0x11
    material.material_count = tex_count
#    
    material.unk0x14 = 0xFF
#    material.unk0x15 = 0x15

    material.color0 = [ bl_mat.material.diffuse_color[0], \
                        bl_mat.material.diffuse_color[1], \
                        bl_mat.material.diffuse_color[2], \
                        1.0 ]
    material.color1 = [ bl_mat.material.specular_color[0], \
                        bl_mat.material.specular_color[1], \
                        bl_mat.material.specular_color[2], \
                        1.0 ]
    material.color2 = [ 1.0, 1.0, 1.0, 1.0 ]
    
    transparency = 0xFF
    if bl_mat.material.use_transparency == True:
        transparency = int(bl_mat.material.alpha * 0xFF)
    
    material.transparency = transparency
    material.vtx_render = vtx_render
    material.texture_indexs = texture_indexs
    material.vtx_descriptor = vtx_attr
    
    return material

#Generate Veretex
def generate_vertex(bm_vtx, loop, bl_loops, bm, bl_tex_slots, obj):
    vtx = Vertex()
    
    #Position
    vtx.pos = [ bm_vtx.co.x, bm_vtx.co.y, bm_vtx.co.z ]
    #Normal
    vtx_idx = loop.index
    print(MSG_INFO_DATA.format('Vertex Index', vtx_idx))
    nrm = bl_loops[vtx_idx].normal
    vtx.nrm = [ nrm[0], nrm[1], nrm[2] ]
    #VERTEXCOLOR0~1
    clr_count = len(bm.loops.layers.color)
    for i in range( 2 if clr_count > 1 else clr_count ):
        clr_lay = bm.loops.layers.color[i]
        clr = loop[clr_lay]
        if i == 0:
            vtx.clr0 = [ clr[0], clr[1], clr[2], clr[3] ]
        if i == 1:
            vtx.clr1 = [ clr[0], clr[1], clr[2], clr[3] ]
    #TEXTURE0~7
    vtx.tex0 = [ 0.0, 0.0 ]
    for i, bl_tex in enumerate(bl_tex_slots):
        # over MAX of UV layers
        if (i > 7):
            break

        # Export UV as first of "UV Maps" at "Data"
        uv_layer = bm.loops.layers.uv[0]
        if ( len(bm.loops.layers.uv) > i):
            # Export UV as index of "UV Maps" at "Data"
            uv_layer = bm.loops.layers.uv[i]
        tex_name = bl_tex.uv_layer
        # if set UV in "Map" at "Mapping"
        if ( len(tex_name) > 0 ):
            # Export UV as index of "Map" at "Texture"
            _idx = obj.data.uv_layers.find(tex_name)
            uv_layer = bm.loops.layers.uv[_idx]

        #flip vertical
        y = -(loop[uv_layer].uv[1] - 1.0)
        uv = [ loop[uv_layer].uv[0], y ]
        if i == 0:
            vtx.tex0 = uv
        if i == 1:
            vtx.tex1 = uv
        if i == 2:
            vtx.tex2 = uv
        if i == 3:
            vtx.tex3 = uv
        if i == 4:
            vtx.tex4 = uv
        if i == 5:
            vtx.tex5 = uv
        if i == 6:
            vtx.tex6 = uv
        if i == 7:
            vtx.tex7 = uv

    return vtx

#Generate Strip
def generate_strip(bm, face, bl_loops, bl_tex_slots, obj, is_16bit):
    print('-Strip')
    strip = Strip()
    strip.cmd = 0x99 if is_16bit else 0x98
    vertexs = []
    
    uv_count = len(bm.loops.layers.uv)
    #Convert Blender's Mesh(bmesh) to DisplayList
    vtx_cnt = len(bl_loops)
    print(MSG_INFO_DATA.format('Vertex Count', vtx_cnt))
    for loop in face.loops:
        bm_vtx = loop.vert
        #Vertex
        vtx = generate_vertex(bm_vtx, loop, bl_loops, bm, bl_tex_slots, obj)
            
        vertexs.append(vtx)
    
    strip.vertexs = vertexs
    strip.count = len(vertexs)
    
    return strip


# Generate DisplayList
def generate_displaylist(bm, mat_idx, bl_loops, bl_tex_slots, obj, is_16bit):
    dlist = DisplayList()
    
    for face in bm.faces:
        if (face.material_index == mat_idx):
            strip = generate_strip(bm, face, bl_loops, bl_tex_slots, obj, is_16bit)
            dlist.strips.append(strip)
    
    return dlist

# Generate DisplatListHeader
def generate_displaylistheader():
    dlist_header = DisplatListHeader()
    
    trans_mtxs = []
    for i in range(8):
        idx = -1
        trans_mtxs.append(idx)
    sizes = [0x00, 0x00]
    dlist_header.trans_mtxs = trans_mtxs
    dlist_header.dlist_sizes = sizes
    
    return dlist_header

# Generate Submesh
def generate_submesh(is_16bit, bm, obj, bl_mat, tex_idx, mat_idx, bl_loops):
    print('-Submesh')
    submesh = Submesh()

    dlist_headers = []
    dlist_header = generate_displaylistheader()
    dlist_headers.append(dlist_header)

    mat_name = bl_mat.name
    bl_tex_slots = list(filter(None, bpy.data.materials[mat_name].texture_slots)) # removes None

    submesh.material = generate_matrial(bm, bl_mat, bl_tex_slots, tex_idx)
    submesh.dlist_headers = dlist_headers
    submesh.boundingsphere_origin = [0.0, 0.0, 0.0]
#    submesh.unk0x3C = 1234.0
    submesh.unk0x40 = 0x14

    # this must be loop (for multiple submesh)
    dlist = generate_displaylist(bm, mat_idx, bl_loops, bl_tex_slots, obj, is_16bit)
    submesh.dlists.append(dlist)
    
    return submesh

#Generate GCMF Attribute
def generate_attribute(is_16bit):
    attribute = Attribute()
    
    #needs someting to decide enableing attribute flags
    #Custom Property?
    
    if (is_16bit == True):
        attribute.is_16bit = True
    
#    if ( ??? == True ) == 1:
#        attribute.is_16bit = True
#    if ( ??? == True ) -== 1:
#        attribute.is_unk0x01 = True
#    if ( ??? == True ) == 1:
#        attribute.is_stiching = True
#    if ( ??? == True ) == 1:
#        attribute.is_skin = True
#    if ( ??? == True ) == 1:
#        attribute.is_effective = True

    return attribute

#Generate Gcmf Object from mesh
def generate_gcmf(is_16bit, obj, idx):
    print(MSG_INFO_INIT.format('Generate GCMF'))
    gcmf = Gcmf()
    
    gcmf.attribute = generate_attribute(is_16bit)
    gcmf.origin = [obj.location[0], obj.location[1], obj.location[2]]
    
    #Radius
    gcmf.boundspher_radius = max(obj.dimensions)
    opaque_count = 0
    transparent_count = 0
    
    # Texture
    # this must be loop by Texture(blender ones) in each Material(blender ones)
    img_names = []
    for image in bpy.data.images:
        img_names.append(image.name)
    for bl_mat in bpy.data.objects[obj.name].material_slots:
        if (bl_mat.material.use_transparency):
            transparent_count = transparent_count + 1
        
        for i, bl_tex in enumerate(bpy.data.materials[bl_mat.name].texture_slots):
            if bl_tex == None:
                #Texture is "None"
                break
            if i > 2:
                print(MSG_WARN_TOO_MANY.format('TEXTURE', i, 3))
                break
            idx = len(gcmf.textures)
            texture = generate_texture(bl_tex, img_names, idx)
            gcmf.textures.append(texture)
    
    print(MSG_INFO_DATA.format('Texture Count', len(gcmf.textures)))    
    opaque_count = len(obj.material_slots) - transparent_count
    
    #Submesh
    bm = bmesh.new()
    
    #Convert to Triangles
    triangulate = False 
    for modifier in obj.modifiers:
        if (modifier.type == 'TRIANGULATE'):
            triangulate = True
    if (triangulate == False):
        #Add 'Triangulate' modifier
        bpy.ops.object.modifier_add(type='TRIANGULATE')
    #Generate "Mesh" with aplly Moddifier
    bl_mesh = obj.to_mesh( bpy.context.scene, True,\
                        calc_tessface=False, settings='RENDER' \
                        )
    if (triangulate == False):
        #Remove 'Triangulate' modifier
        bpy.ops.object.modifier_remove(modifier='Triangulate')
    
    #Generate Bmesh
    bm.from_mesh(bl_mesh)
    #Apply Transform (Scale/Rotation/Translation)
    bmesh.ops.transform(bm, matrix=obj.matrix_world, verts=bm.verts)
    #Rotate -90 deg (Swap Y-axis and Z-axis)
    rot = mathutils.Matrix.Rotation(math.radians(-90), 4, (1.0, 0.0, 0.0))
    bmesh.ops.rotate(bm, cent=(0.0, 0.0, 0.0), matrix=rot, verts=bm.verts)
     #Convert to Triangles
    bmesh.ops.triangulate(bm, faces=bm.faces)
    
    bm.to_mesh(bl_mesh)
    #Generat custom-split normals
    bl_mesh.use_auto_smooth = True
    bl_mesh.calc_normals_split()
    bl_loops = bl_mesh.loops
    tex_idx = 0
    for mat_idx, bl_mat in enumerate(obj.material_slots):
        submesh = generate_submesh(is_16bit, bm, obj, bl_mat, tex_idx, mat_idx, bl_loops)
        gcmf.submeshs.append(submesh)
        tex_idx = tex_idx + submesh.material.material_count
    
#    # Matrix
#    for i in range(1):
#        mtx = generate_matrix()
#        gcmf.mtxs.append(mtx)
    
    mtx_idxs = []
    for i in range(8):
        mtx_idxs.append(-1)
    gcmf.mtx_idxs = mtx_idxs
    
    # flash bmesh
    del bm
    
    gcmf.texture_count = len(gcmf.textures)
    gcmf.opaque_count = opaque_count
    gcmf.transparent_count = transparent_count
    
    return gcmf

#Generate GcmfEntry
def generate_gcmfentry(is_16bit, obj, idx):
    entry = GcmfEntry()
    entry.gcmf = generate_gcmf(is_16bit, obj, idx)
    entry.name = obj.name
    
    return entry

#Export gma
def save(filepath, little_endian=False, is_16bit=False):
    with open(filepath, 'wb') as file:
        #Set Endian
        if little_endian == True:
            sel_endian = '<'
        else:
            sel_endian = '>' 
        
        gma = Gma()
        for i, obj in enumerate(bpy.context.selected_objects):
            if (len(obj.material_slots) < 1):
                print(MSG_WARN_NONE_MAT.format(obj.name))
                #Skip Mesh Export
                continue
            #gcmf entry
            entry = generate_gcmfentry(is_16bit, obj, i)
            gma.entrys.append(entry)
            
        gma.pack(file, sel_endian)
    
    file.close()