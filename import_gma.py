import array

import bmesh
import bpy
import mathutils
import numpy

from .gma import Gma
from .gcmf import VertexAttribute

#Messages
MSG_INFO_INIT = '---- {0} ----'
MSG_INFO_DATA = '{0}: {1}'
MSG_INFO_DATA_HEX = '{0}: {1:#X}'

#Names
NAME_MATERIAL = 'material_{0:03}'
NAME_TEXTURE = 'gxtex_{0:03}'
NAME_TPL_COMMON = 'tpl_common_{0:03}'
NAME_TPL = 'tpl_{0:03}'
NAME_POLYGON = 'polygon_{0}'
NAME_ARMATURE = '{0}_armature'
NAME_NODE = 'node_{0}'
NAME_VERTEXCOLOR = 'color{0}'
NAME_UV = 'uv{0}'

#Storage Mesh datas
class Mesh_data:
    def __init__(self):
        self.normals = [] #Collect for "Custom Split Normals"
        self.color0s = []
        self.color1s = []
        self.tex0s = []
        self.tex1s = []
        self.tex2s = []
        self.tex3s = []
        self.tex4s = []
        self.tex5s = []
        self.tex6s = []
        self.tex7s = []


#Generate Blender's Material
#TODO: something ways to store import GMA values
def generate_material(material, matid, texs, gcmf_texs, is_alpha):
    flag = material.vtx_descriptor
    mat = bpy.data.materials.new(name=NAME_MATERIAL.format(matid))
    #Material Color
    mat.diffuse_color = mathutils.Vector((\
                            material.color0[0], \
                            material.color0[1], \
                            material.color0[2]))
    mat.specular_color = mathutils.Vector((\
                            material.color1[0], \
                            material.color1[1], \
                            material.color1[2]))
    #Emit
    mat.emit = material.emission / 0xFF
    #Alpha
    mat.use_transparency = True
    if is_alpha:
        mat.alpha = 0.0
    else:
        mat.alpha = material.transparency / 0xFF
    #VertexColor
    if flag.gx_va_clr0 == True or flag.gx_va_clr1 == True:
        mat.use_vertex_color_paint = True
    #Texture
    
    for i, texid in enumerate(material.texture_indexs):
        if texid >= 0 and len(texs) > texid:
            mat.active_texture_index = i
            mat.active_texture = texs[texid]
            tex_slot = mat.texture_slots[i]
            #UV
            tex_slot.uv_layer = NAME_UV.format(i)
            tex = gcmf_texs[texid]
            #Mapping
            if tex.uv_wrap.unknown0:
                tex_slot.texture_coords = 'REFLECTION'
            # if tex.unk0x00.unknown4 or i >= 2:
            if tex.unk0x00.unknown4:
                tex_slot.texture_coords = 'NORMAL'
            #Blend
            if i == 0:
                tex_slot.blend_type = 'MIX'
            else:
                tex_slot.blend_type = 'ADD'
            #Strangth (Maybe)
            tex_slot.use_map_diffuse = True
            tex_slot.diffuse_factor = tex.unk0x0C / 0xFF
            
            if is_alpha:
                tex_slot.use_map_alpha = True


    return mat


#Generate Blender's UV
def generate_uv(mesh, channel_name, uvs):
    try:
        mesh.uv_layers[channel_name].data
    except:
        #Generate UV
        mesh.uv_textures.new(channel_name) # 2.7
    for i, loop in enumerate(mesh.loops):
        mesh.uv_layers[channel_name].data[i].uv = uvs[loop.vertex_index]


#Generate Blender's VertexColor
def generate_vertexcolor(mesh, color_name, vcolors):
    try:
        mesh.vertex_colors[color_name].data
    except:
        #Generate VertexColor
        mesh.vertex_colors.new(name=color_name)
    for i, loop in enumerate(mesh.loops):
        mesh.vertex_colors[color_name].data[i].color = vcolors[loop.vertex_index]


#Generate Blender's Texture
def generate_texture(texture, texid, images):
    tex_name = NAME_TEXTURE.format(texid)
    tex = bpy.data.textures.new(name=tex_name, type='IMAGE')
    
    #Wrap
    #GMA    : Blender
    #CLAMP  : EXTEND
    #REPEAT : REPEAT
    #MIRROR : REPEAT and MIRROR
    tex.extension = 'EXTEND'
    #Wrap Repeat X/Y and Mirror X/Y
    if texture.uv_wrap.repeat_x or \
    texture.uv_wrap.repeat_y or \
    texture.uv_wrap.mirror_x or \
    texture.uv_wrap.mirror_y:
        tex.extension = 'REPEAT'
    #Wrap Mirror X
    if texture.uv_wrap.mirror_x:
        tex.use_mirror_x = True
    #Wrap Mirror Y
    if texture.uv_wrap.mirror_y:
        tex.use_mirror_y = True

    #Image
    imgid = texture.texture_index
    if imgid >= 0:
        if texture.unk0x00.commontex:
            name = NAME_TPL_COMMON.format(imgid)
        else:
            name = NAME_TPL.format(imgid)
        try:
            images[name]
        except:
            #Generate Empty Texture Image
            #for unloadable index Texture image
            image = bpy.data.images.new(name, width=1, height=1)
            image.source = 'FILE'
            filepath = name
            images[name] = image
        tex.image = images[name]
    return tex


#Generate mesh from Gcmf Object
def generate_mesh(mesh, bm, matid, mesh_data, dlist, mtxidxs, mtxs, first_iscw):
    v0 = mathutils.Vector(( 0, 0, 0 ))
    v1 = mathutils.Vector(( 0, 0, 0 ))
    v2 = mathutils.Vector(( 0, 0, 0 ))
    iscw = first_iscw
    for strip in dlist.strips:
        for i, vertex in enumerate(strip.vertexs):
            vtx = mathutils.Vector(( vertex.pos[0], vertex.pos[1], vertex.pos[2] ))
            #Point_Normal_Matrix Index
            pnmtxidx = vertex.pnmtxidx
            if (pnmtxidx >= 0):
                if (pnmtxidx > 0x18) or ((pnmtxidx % 3) != 0):
                    print(MSG_INFO_DATA.format('pnmtxidx', pnmtxidx))
                else:
                    ridx = int((pnmtxidx/3)-1)
                    print(ridx)
                    idx = mtxidxs[ridx]
                    if idx < 0:
                        print(MSG_INFO_DATA.format('matrix_index', idx))
                    else:
                        mtx = mtxs[idx].mtx
                        vtx = mtx * vtx
            #Generate Vertex
            v = bm.verts.new(vtx)
            #Normal
            vec = mathutils.Vector(( vertex.nrm[0], vertex.nrm[1], vertex.nrm[2] ))
            v.normal = vec
            mesh_data.normals.append(vec.normalized())
            #Color 0
            clr = mathutils.Vector(( vertex.clr0[0], vertex.clr0[1], vertex.clr0[2], vertex.clr0[3] ))
            mesh_data.color0s.append(clr)
            #Color 1
            clr = mathutils.Vector(( vertex.clr1[0], vertex.clr1[1], vertex.clr1[2], vertex.clr1[3] ))
            mesh_data.color1s.append(clr)
            #UV0
            tex = mathutils.Vector(( vertex.tex0[0], -(vertex.tex0[1] - 1.0) ))
            mesh_data.tex0s.append(tex)
            #UV1
            tex = mathutils.Vector(( vertex.tex1[0], -(vertex.tex1[1] - 1.0) ))
            mesh_data.tex1s.append(tex)
            #UV2
            tex = mathutils.Vector(( vertex.tex2[0], -(vertex.tex2[1] - 1.0) ))
            mesh_data.tex2s.append(tex)
            #UV3
            tex = mathutils.Vector(( vertex.tex3[0], -(vertex.tex3[1] - 1.0) ))
            mesh_data.tex3s.append(tex)
            #UV4
            tex = mathutils.Vector(( vertex.tex4[0], -(vertex.tex4[1] - 1.0) ))
            mesh_data.tex4s.append(tex)
            #UV5
            tex = mathutils.Vector(( vertex.tex5[0], -(vertex.tex5[1] - 1.0) ))
            mesh_data.tex5s.append(tex)
            #UV6
            tex = mathutils.Vector(( vertex.tex6[0], -(vertex.tex6[1] - 1.0) ))
            mesh_data.tex6s.append(tex)
            #UV7
            tex = mathutils.Vector(( vertex.tex7[0], -(vertex.tex7[1] - 1.0) ))
            mesh_data.tex7s.append(tex)
            
            #Generate Face
            if i == 0:
                iscw = first_iscw
            #Generate Vertex
            if i > 1:
                v2 = v
                if iscw == True:
                    face = bm.faces.new((v2, v1, v0))
                    iscw = False
                else:
                    face = bm.faces.new((v0, v1, v2))
                    iscw = True
                face.material_index = matid
                v0 = v1
                v1 = v2
            elif i == 1:
                v1 = v
            elif i == 0:
                v0 = v
    bm.to_mesh(mesh)   


#Import gma
def load(filepath, little_endian=False):
    with open(filepath, 'rb') as file:
        #Set Endian
        if little_endian == True:
            sel_endian = '<'
        else:
            sel_endian = '>'
        
        #Genarate GMA object
        gma = Gma()
        #Read GMA from file
        gma.unpack(file, sel_endian)
        #Read TPL from file
        #TODO read TPL
        images = {}
        
        texid = 0
        
        #Generate Mesh
        for i, entry in enumerate(gma.entrys):
            print(MSG_INFO_INIT.format('Generate Blender Mesh'))
            print(MSG_INFO_DATA.format('Mesh Name', entry.name))
            mesh_name = NAME_POLYGON.format(i)
            mesh = bpy.data.meshes.new(mesh_name)
            obj = bpy.data.objects.new(entry.name, mesh)
            
            scene = bpy.context.scene
            scene.objects.link(obj)
            scene.objects.active = obj
            obj.select = True

            bm = bmesh.new()
            gcmf = entry.gcmf
            mesh_data = Mesh_data() # Store Normals, UVs, VertexColors
            
            flags = numpy.array(0x00, dtype='i4')
            total_flags = numpy.array(0x00, dtype='i4')
            
            # Texture
            print(MSG_INFO_DATA.format('Texture Count', len(gcmf.textures)))
            texs = []
            for texture in gcmf.textures:
                tex = generate_texture(texture, texid, images)
                texs.append(tex)
                texid = texid + 1
            gcmf_texs = gcmf.textures
            
            
            mtxidxs = gcmf.mtx_idxs
            print('Matrix Indexies') #
            for mtxidx in mtxidxs:
                print(MSG_INFO_DATA.format('mtxidx', mtxidx))
            mtxs = gcmf.mtxs
            print(MSG_INFO_DATA.format('Matrix Count', len(mtxs)))
            
            print(MSG_INFO_DATA.format('Submesh Count', len(gcmf.submeshs)))
            for matid, submesh in enumerate(gcmf.submeshs):
                #Vertex Attribute
                attribute = submesh.material.vtx_descriptor
                flags = attribute.pack()
                #Store all submesh's attribute
                total_flags = flags | total_flags
                for i, dlist in enumerate(submesh.dlists):
                    is_cw = (i % 2 == 1)
                    #even : ccw
                    #odd  : cw
                    generate_mesh(mesh, bm, matid, mesh_data, dlist, mtxidxs, mtxs, is_cw)
            
            #Generate Vertex_Attribute from all submeshs's vertex_attribute
            all_attribute = VertexAttribute()
            all_attribute.unpack(total_flags)
            mesh.update()
            
            if total_flags != numpy.array(0x00, dtype='u4'):
                print(MSG_INFO_DATA_HEX.format('total_flags', total_flags))
            
            
            #Normal
            if all_attribute.gx_va_nrm == True:
                clnors = array.array('f', [0.0] * (len(mesh.loops) * 3))
                mesh.loops.foreach_get("normal", clnors)
                mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))
                
                mesh.use_auto_smooth = True
                mesh.normals_split_custom_set_from_vertices(mesh_data.normals)
            #Color0
            if all_attribute.gx_va_clr0 == True:
                color_name = NAME_VERTEXCOLOR.format(0)
                generate_vertexcolor(mesh, color_name, vcolors=mesh_data.color0s)
            #Color1
            if all_attribute.gx_va_clr1 == True:
                color_name = NAME_VERTEXCOLOR.format(1)
                generate_vertexcolor(mesh, color_name, vcolors=mesh_data.color1s)
            #UV0
            if all_attribute.gx_va_tex0 == True:
                channel_name = NAME_UV.format(0)
                generate_uv(mesh, channel_name, uvs=mesh_data.tex0s)
            #UV1
            if all_attribute.gx_va_tex1 == True:
                channel_name = NAME_UV.format(1)
                generate_uv(mesh, channel_name, uvs=mesh_data.tex1s)
            #UV2
            if all_attribute.gx_va_tex2 == True:
                channel_name = NAME_UV.format(2)
                generate_uv(mesh, channel_name, uvs=mesh_data.tex2s)
            #UV3
            if all_attribute.gx_va_tex3 == True:
                channel_name = NAME_UV.format(3)
                generate_uv(mesh, channel_name, uvs=mesh_data.tex3s)
            #UV4
            if all_attribute.gx_va_tex4 == True:
                channel_name = NAME_UV.format(4)
                generate_uv(mesh, channel_name, uvs=mesh_data.tex4s)
            #UV5
            if all_attribute.gx_va_tex5 == True:
                channel_name = NAME_UV.format(5)
                generate_uv(mesh, channel_name, uvs=mesh_data.tex5s)
            #UV6
            if all_attribute.gx_va_tex6 == True:
                channel_name = NAME_UV.format(6)
                generate_uv(mesh, channel_name, uvs=mesh_data.tex6s)
            #UV7
            if all_attribute.gx_va_tex7 == True:
                channel_name = NAME_UV.format(7)
                generate_uv(mesh, channel_name, uvs=mesh_data.tex7s)
            
            #Material
            for matid, submesh in enumerate(gcmf.submeshs):
                material = submesh.material
                #Is Alpha
                is_alpha = matid >= gcmf.opaque_count
                mat = generate_material(material, matid, texs, gcmf_texs, is_alpha)
                obj.data.materials.append(mat)
            
            bm.free()
            mesh.update()
            #Rotate X-axis 90deg
            bpy.context.object.rotation_euler[0] = 1.5708
            
            #Transform to Node
            if bpy.context.mode == 'EDIT_ARMATURE':
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                
            if(len(gcmf.mtxs) > 0):
                #Add Armature
                bpy.ops.object.add(type='ARMATURE', location = (0, 0 ,0), enter_editmode=False)
                armature_name = NAME_ARMATURE.format(entry.name)
                bpy.context.object.name = armature_name

                for j, matrix in enumerate(gcmf.mtxs):
                    #Edit Mode
                    bpy.ops.object.mode_set(mode='EDIT')
                    #Instatiate Bone
                    name = NAME_NODE.format(j)
                    b = bpy.context.object.data.edit_bones.new(name)
                    #Apply Matrix to EditBone object
                    b.head = mathutils.Vector((0.0, 0.0, 0.0))
                    b.tail = mathutils.Vector((0.0, 0.1, 0.0))
                    b.transform(matrix.mtx, scale=True, roll=True)
                    
                #Object Mode
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                bpy.context.object.rotation_euler[0] = 1.5708

    file.close()
    bpy.ops.object.shade_smooth()