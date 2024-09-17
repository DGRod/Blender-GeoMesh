# Ensure that Blender has access to the .venv with GDAL installed
import sys
venv_path = "C:\\Users\\DGRod\\Onedrive\\Desktop\\Python Code\\Blender GeoMesh\\.venv\\Lib\\site-packages" 
if venv_path not in sys.path:
    sys.path.append(venv_path)

# Import Blender modules
import bpy
import bmesh

# Import GDAL and math tools
from osgeo import gdal
gdal.UseExceptions()
import numpy as np
import pandas as pd
import math





class GEOMESH_OT_RASTER_MODEL(bpy.types.Operator):
    """Import and model a Raster file"""
    bl_label = "Model Raster (TIFF/XYZ)"
    bl_idname = "geomesh.raster_model"
    bl_options = {"REGISTER", "UNDO"}

    # Store filepath to Raster here
    filepath: bpy.props.StringProperty(default="")

    # Filter file browser for TIFF or XYZ files
    filter_glob: bpy.props.StringProperty(
        default="*.tif;*.xyz",
        options={"HIDDEN"})
    
    # Settings for Raster import
    z_factor: bpy.props.FloatProperty(name="Vertical Exaggeration", default=1, min=0, max=100)
    scale: bpy.props.IntProperty(name="Scale", default=100, min=1, max=1000)
    multires: bpy.props.BoolProperty(name="Apply Multiresolutin Modifier", default=False)
       

    # Draw the Settings window
    def draw(self, context):
        print("drawing", context)
        layout = self.layout
        layout.prop(self, "z_factor")
        layout.prop(self, "scale")
        layout.prop(self, "multires")


    def invoke(self, context, event):
        # Set default input settings
        self.z_factor = 1
        self.scale = 100
        print("invoking", context)
        # Ask the user to select a Raster file
        bpy.context.window_manager.fileselect_add(self)
        print(self.filepath)

        return {"RUNNING_MODAL"}
    



    def execute(self, context):
        print("executing", context)
        # print(self.filepath)
        # If filetype is .tif, translate data into DataFrame:
        if self.filepath[-4:] == ".tif":
            # Open a DataSet with GDAL
            ds = gdal.Open(self.filepath)
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
        if self.filepath[-4:] == ".xyz":
            # Get Raster dimensions
            ds = gdal.Open(self.filepath)
            xsize = ds.RasterXSize
            ysize = ds.RasterYSize
            # Close DataSet
            ds = None

            # Open .XYZ as a DataFrame
            df = pd.read_csv(self.filepath, sep=" ", header=None)
            df.columns = ["x", "y", "z"]
        

        # Get minimum coordinate values to place Raster at World Origin
        mins = df.min()
        xmin = mins["x"]
        ymin = mins["y"]
        zmin = mins["z"]

        # Create Tuples of all x, y, z coordinate triplets, 
        coords = [((x - xmin)/self.scale, (y - ymin)/self.scale, (self.z_factor * (z - zmin))/self.scale) for x, y, z in zip(df["x"], df["y"], df["z"])]
        
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
    