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
    from .addon.register import register_addon
    register_addon()

def unregister():
    from .addon.register import unregister_addon
    unregister_addon()