# Ensure that Blender has access to the .venv with GDAL installed
import sys
venv_path = "C:\\Users\\DGRod\\Onedrive\\Desktop\\Python Code\\Blender GeoMesh\\.venv\\Lib\\site-packages" 
if venv_path not in sys.path:
    sys.path.append(venv_path)

# Import Blender modules
import bpy
import bmesh
from bpy_extras.io_utils import ImportHelper

# Import GDAL and math tools
from osgeo import gdal
import numpy as np
import pandas as pd
import csv





class GEOMESH_OT_RASTER_MODEL(bpy.types.Operator, ImportHelper):
    """Import and model a Raster file"""
    bl_label = "Model Raster (TIFF)"
    bl_idname = "geomesh.raster_model"

    # Store filepath to Raster here
    fn: bpy.props.StringProperty(name="")
    # Filter file browser for TIFF files
    filter_glob: bpy.props.StringProperty(
        default="*.tif;*.xyz",
        options={"HIDDEN"})
    

    def execute(self, context):
        # Ask the user to select a Raster file
        self.fn = self.filepath
        
        # Open Raster with GDAL
        # ds = gdal.Open(self.fn)
        # gt = ds.GetGeoTransform()
        # proj = ds.GetProjection()
        
        # If filetype is .xyz
        if self.fn[-4:] == ".xyz":
            # df = pd.read_csv(self.fn, sep=" ", header=None)
            # df.to_csv("C:\\Users\\DGRod\\OneDrive\\Desktop\\Python Code\\Blender GeoMesh\\GeoMesh\\addon\\operator\\data\\mesh_data.csv", index=False, header=None, sep=",")
            ds = gdal.Open(self.fn)
            band = ds.GetRasterBand(1)
            array = band.ReadAsArray()

            mesh_obj = bpy.ops.mesh.primitive_plane_add(size=100)
            #bpy.context.collection.link(mesh_obj)
            # mesh_obj.select_set(state=True)
            # bpy.context.view_layer.objects.active = mesh_obj
            bm = bmesh.new()
            bm.from_mesh(bpy.context.object.data)
            
            for row in array:
                print("row", row)
                bm.verts.new(coord)
            
            bm.to_mesh(mesh_obj)
            bm.free()
        
        
        return {"FINISHED"}
    