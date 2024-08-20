import bpy
import importlib

from . import export_gma
from . import import_gma
from . import import_gml

bl_info= {
    "name": "Amusement Vision GMA format",
    "author": "CH-MCL",
    "version": (0, 3, 279, 1),
    "blender": (2, 79, 0),
    "location": "File > Import-Export > Amusement Vision Model (.gma)",
    "description": "Imports a Amusement Vision 3d model.",
    "category": "Import-Export",
}

if "bpy" in locals():
    import importlib
    if "import_gma" in locals():
        importlib.reload(import_gma)
    if "export_gma" in locals():
        importlib.reload(export_gma)
    if "import_gml" in locals():
        importlib.reload(import_gml)

from bpy.props import (
        BoolProperty,
        #FloatProperty,
        StringProperty,
        #EnumProperty,
        )
from bpy_extras.io_utils import (
#        ImportHelper,
        ExportHelper,
#        orientation_helper_factory,
#        path_reference_mode,
#        axis_conversion,
        )


#Import GMA
class IMPORT_UL_GMA(bpy.types.Operator):
    bl_idname = "import_scene.gma"
    bl_label = "Import GMA"
    bl_description = "Import a Amusement Vision 3D model"
    bl_options = {'REGISTER', 'UNDO'}

    little_endian = BoolProperty(
            name="Little Endian",
            description="Read file as Little Endian. Super Monkey Ball Delux's gma must Enable this. ",
            default=False,
            )

    filepath = StringProperty(
        name="File Path",
        description="Filepath used for importing the GMA file.",
        maxlen=1024)
    filter_glob = StringProperty(default="*.gma", options={'HIDDEN'})

    def execute(self, context):
        keywords = self.as_keywords()
        import_gma.load(self.filepath, self.little_endian)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


#Export GMA
class EXPORT_UL_GMA(bpy.types.Operator, ExportHelper):
    bl_idname = "export_scene.gma"
    bl_label = "Export GMA"
    bl_description = "Export a Amusement Vision model"
    bl_options = {'REGISTER', 'UNDO'}

    little_endian = BoolProperty(
            name="Little Endian",
            description="Write as Little Endian. Super Monkey Ball Delux's gma must Enable this.",
            default=False,
            )
    is_16bit = BoolProperty(
            name="16bit Vertex",
            description="Write Vertex as 16bit"
                        "Make DisplayList size to 1/2",
            default=False,
            )
    filename_ext = ".gma"
    filepath = StringProperty(
        name="File Path", 
        description="Filepath used for importing the GMA file.", 
        maxlen=1024)
    filter_glob = StringProperty(default="*.gma", options={'HIDDEN'})

    def execute(self, context):
        export_gma.save(self.filepath, self.little_endian, self.is_16bit)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


#Import GML
class IMPORT_UL_GML(bpy.types.Operator):
    bl_idname = "import_scene.gml"
    bl_label = "Import GML"
    bl_description = "Import a Amusement Vision 3D model (alt). This file is used at Virtua Striker."
    bl_options = {'REGISTER', 'UNDO'}

    little_endian = BoolProperty(
            name="Little Endian",
            description="Read file as Little Endian. Super Monkey Ball Delux's gma must Enable this.",
            default=False,
            )
    
    filepath = StringProperty(
        name="File Path",
        description="Filepath used for importing the GML file."
                    "Used at Virtua Striker",
        maxlen=1024)
    filter_glob = StringProperty(default="*.gml", options={'HIDDEN'})

    def execute(self, context):
        keywords = self.as_keywords()
        import_gml.load(self.filepath, self.little_endian)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}
#no plans exporting GML


def menu_func_import(self, context):
    self.layout.operator(IMPORT_UL_GMA.bl_idname, text="Amusement Vision Model (.gma)")
    self.layout.operator(IMPORT_UL_GML.bl_idname, text="Amusement Vision Model alt(.gml)")


def menu_func_export(self, context):
    self.layout.operator(EXPORT_UL_GMA.bl_idname, text="Amusement Vision Model (.gma)")
    #no plans export GML


classes = (
    IMPORT_UL_GMA,
    EXPORT_UL_GMA,
    IMPORT_UL_GML,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
    