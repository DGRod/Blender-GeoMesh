# Ensure that Blender has access to the .venv with GDAL installed
import sys
venv_path = "C:\\Users\\DGRod\\Onedrive\\Desktop\\Python Code\\Blender GeoMesh\\.venv\\Lib\\site-packages" 
if venv_path not in sys.path:
    sys.path.append(venv_path)

# Import Blender modules
import bpy
from bpy_extras.io_utils import ImportHelper

# Import GDAL and Numpy
from osgeo import gdal
import numpy as np


print(gdal.__version__)
print(sys.executable)
class GEOMESH_OT_RASTER_MODEL(bpy.types.Operator, ImportHelper):
    """Import and model a Raster file"""
    bl_label = "Model Raster"
    bl_idname = "geomesh.raster_model"

    # Store filepath to Raster here
    fn: bpy.props.StringProperty(name="")

    def execute(self, context):
        # Ask the user to select a Raster file
        self.fn = self.filepath
        
        ds = gdal.Open(self.fn)
        gt = ds.GetGeoTransform()
        proj = ds.GetProjection()

        band = ds.GetRasterBand(1)
        array = band.ReadAsArray()

        print(gt, proj, array)

        for point in array:
            print("point", point)

        return {"FINISHED"}
    