import bpy
from .raster_model import GEOMESH_OT_RASTER_MODEL

class OBJECT_PT_GeoMesh(bpy.types.Panel):
    """Creates a panel on the sidebar"""
    bl_label = "GeoMesh GIS Tools"
    bl_idname = "OBJECT_PT_GeoMesh"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GeoMesh"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator('geomesh.raster_model')