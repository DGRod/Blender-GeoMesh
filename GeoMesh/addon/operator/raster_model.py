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
import math





class GEOMESH_OT_RASTER_MODEL(bpy.types.Operator, ImportHelper):
    """Import and model a Raster file"""
    bl_label = "Model Raster (TIFF/XYZ)"
    bl_idname = "geomesh.raster_model"

    # Store filepath to Raster here
    fn: bpy.props.StringProperty(name="")

    # Filter file browser for TIFF or XYZ files
    filter_glob: bpy.props.StringProperty(
        default="*.tif;*.xyz",
        options={"HIDDEN"})
    

    def execute(self, context):
        # Ask the user to select a Raster file
        self.fn = self.filepath
        
        # If filetype is .tif, translate data into DataFrame:
        if self.fn[-4:] == ".tif":
            # Open a DataSet with GDAL
            ds = gdal.Open(self.fn)
            # Get list of values from the DataSet
            array = ds.GetRasterBand(1).ReadAsArray()
            flat_array = array.flatten()
            # Get coordinate data from the DataSet
            gt = ds.GetGeoTransform()
            res = gt[1]
            xmin = gt[0]
            ymax = gt[3]
            xsize = ds.RasterXSize
            ysize = ds.RasterYSize
            xstart = xmin + (res / 2)
            ystart = ymax - (res / 2)
            # Close the DataSet
            ds = None

            # Create columns for a DataFrame
            x = np.arange(xstart, xstart + (res * xsize), res, dtype=int)
            y = np.arange(ystart, ystart - (res * ysize), -res, dtype=int)
            x = np.tile(x, ysize)
            y = np.repeat(y, xsize)

            # Create a DataFrame with the columns and values
            df = pd.DataFrame({"x":x, "y":y, "z":flat_array})

        

        # If filetype is .xyz, paste data into DataFrame:
        if self.fn[-4:] == ".xyz":
            # Get Raster dimensions
            ds = gdal.Open(self.fn)
            xsize = ds.RasterXSize
            ysize = ds.RasterYSize
            # Close DataSet
            ds = None

            # Open .XYZ as a DataFrame
            df = pd.read_csv(self.fn, sep=" ", header=None)
            df.columns = ["x", "y", "z"]
        

        # Get minimum coordinate values to place Raster at World Origin
        mins = df.min()
        xmin = mins["x"]
        ymin = mins["y"]
        zmin = mins["z"]

        # Create Tuples of all x, y, z coordinate triplets, 
        coords = [((x - xmin)/100, (y - ymin)/100, (z - zmin)/100) for x, y, z in zip(df["x"], df["y"], df["z"])]
        
        # Create a Grid object with the same number of vertices as the Raster
        bpy.ops.mesh.primitive_grid_add(x_subdivisions=xsize - 1, y_subdivisions=ysize - 1) 
        # Make sure Blender is in Object Mode
        bpy.ops.object.mode_set(mode="OBJECT")
        # Grab the mesh data of the newly-created Grid object
        mesh_data = bpy.context.object.data

        # Create a new BMesh and assign mesh_data to it
        bm = bmesh.new()
        bm.from_mesh(mesh_data)
        # Overwrite the coordinates for each vertex in the Grid
        for vertex, coord in zip(bm.verts, coords):
            vertex.co = coord
        
        # Send BMesh data back to mesh_data
        bm.to_mesh(mesh_data)
        bm.free()
        

        return {"FINISHED"}
    