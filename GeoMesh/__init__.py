bl_info = {
    "name": "GeoMesh",
    "description": "GeoMesh GIS Tools",
    "author": "DGRod",
    "version": (1, 0),
    "blender": (4, 2, 1),
    "location": "View3D",
    "category": "3D View"
}

def register():
    from .addon.geomesh_raster_model import register
    register()

def unregister():
    from .addon.geomesh_raster_model import unregister
    unregister()