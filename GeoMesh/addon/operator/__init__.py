import bpy

from .raster_model import GEOMESH_OT_RASTER_MODEL

classes = (
    GEOMESH_OT_RASTER_MODEL,
)

def register_operators():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister_operators():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)