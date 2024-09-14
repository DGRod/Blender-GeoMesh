import bpy

class GEOMESH_OT_RASTER_MODEL(bpy.types.Operator):
    """Import and model a Raster file"""
    bl_label = "Raster Model"
    bl_idname = "geomesh.raster_model"

    def execute(self, context):
        print("Importing Raster")
        return {"FINISHED"}
    