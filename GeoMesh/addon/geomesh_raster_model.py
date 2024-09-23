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





class GEOMESH_OT_FILE_BROWSER(bpy.types.Operator):
    """Import a Raster file (TIFF/XYZ)"""
    bl_idname = "geomesh.file_browser"
    bl_label = "Import Raster"
    bl_options = {"REGISTER", "UNDO"}

    # Store the filepath
    filepath: bpy.props.StringProperty(name="File Path", subtype="FILE_PATH")
    # Filter file browser for TIFF or XYZ files
    filter_glob: bpy.props.StringProperty(
        default="*.tif;*.xyz",
        options={"HIDDEN"})

    def invoke(self, context, event):
        # Call the file browser window
        bpy.context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}
    
    def execute(self, context):
        # Set the GEOMESH_Props filepath to the selected file
        bpy.context.scene.geomesh.filepath = self.filepath
        # Call raster_model
        bpy.ops.geomesh.raster_model("INVOKE_DEFAULT")
        return {"FINISHED"}
    





class GEOMESH_OT_RASTER_MODEL(bpy.types.Operator):
    """Model a Raster file (TIFF/XYZ)"""
    bl_label = "Model Raster (TIFF/XYZ)"
    bl_idname = "geomesh.raster_model"
    bl_options = {"REGISTER", "UNDO"}

    # Store filepath to Raster
    filepath: bpy.props.StringProperty(name="File Path", subtype="FILE_PATH")
    
    # Settings for Raster import
    z_factor: bpy.props.FloatProperty(name="Z-Factor", default=1, min=0, max=100)
    scale: bpy.props.FloatProperty(name="Scale", default=1, min=0.01, max=100)
    multires: bpy.props.BoolProperty(name="Apply Multiresolution Modifier", default=False)

    @classmethod
    def poll(self, context):
        active = context.active_object
        selected = context.selected_objects
        # Check if there are no active/selected objects, or that the active object is selected
        return not active or (active in selected) or selected == []
    
    def invoke(self, context, event):
        # Set raster settings to default values
        geomesh = context.scene.geomesh
        geomesh.z_factor = 1
        geomesh.scale = 1
        geomesh.multires = False
        return self.execute(context)
       

    def execute(self, context):
        geomesh = context.scene.geomesh
        self.filepath = geomesh.filepath

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
        coords = [((x - xmin) * (self.scale/100), (y - ymin) * (self.scale/100), (self.z_factor * (z - zmin)) * (self.scale/100)) for x, y, z in zip(df["x"], df["y"], df["z"])]

        # If there is no active object:
        if not context.active_object or context.active_object not in context.selected_objects:
            # Create a Grid object with the same number of vertices as the Raster
            bpy.ops.mesh.primitive_grid_add(x_subdivisions=xsize - 1, y_subdivisions=ysize - 1)
            # Make sure Blender is in Object Mode
            bpy.ops.object.mode_set(mode="OBJECT")

        # Grab the mesh data of the newly-created Grid object
        mesh_data = context.active_object.data
        
        # Create a new BMesh and assign mesh_data to it
        bm = bmesh.new()
        bm.from_mesh(mesh_data)
        # Overwrite the coordinates for each vertex in the Grid
        for vertex, coord in zip(bm.verts, coords):
            vertex.co = coord
        # Send BMesh data back to mesh_data
        bm.to_mesh(mesh_data)
        bm.free()

        # Apply multiresolution modifier to smooth the raster:
        if self.multires == True and "Multires" not in context.active_object.modifiers.keys():
            bpy.ops.object.modifier_add(type="MULTIRES")
            bpy.ops.object.multires_subdivide(modifier="Multires", mode="CATMULL_CLARK")
            context.active_object.modifiers[-1].levels = 1
                
        return {"FINISHED"}
    


class OBJECT_PT_GeoMesh(bpy.types.Panel):
    """Creates a panel on the sidebar"""
    bl_label = "GeoMesh GIS Tools"
    bl_idname = "OBJECT_PT_GeoMesh"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GeoMesh"

    def draw(self, context):
        # Draw the GeoMesh panel
        geomesh = context.scene.geomesh
        layout = self.layout
        layout.operator('geomesh.file_browser')
        row = layout.row()
        # Check if an object is selected
        if context.active_object in context.selected_objects:
            layout.prop(geomesh, "z_factor")
            layout.prop(geomesh, "scale")
            layout.prop(geomesh, "multires")
        else:
            layout.label(icon="ERROR", text="No raster selected")


# Call raster_model whenever a geomesh property is updated
def call_raster(self, context):
    geomesh = context.scene.geomesh
    if context.active_object:
        print("calling raster")
        bpy.ops.geomesh.raster_model(z_factor=geomesh.z_factor, scale=geomesh.scale, multires=geomesh.multires)



class GEOMESH_Props(bpy.types.PropertyGroup):

    filepath: bpy.props.StringProperty(name="File Path", subtype="FILE_PATH")

    z_factor: bpy.props.FloatProperty(name="Vertical Exaggeration", default=1, min=0, max=100, update=call_raster)
    
    scale: bpy.props.FloatProperty(name="Scale", default=1, min=0.01, max=100, update=call_raster)

    multires: bpy.props.BoolProperty(name="Apply Multiresolution Modifier", default=False, update=call_raster)


# Register Addon
classes = {
    GEOMESH_Props,
    GEOMESH_OT_FILE_BROWSER,
    GEOMESH_OT_RASTER_MODEL,
    OBJECT_PT_GeoMesh,
}

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.geomesh = bpy.props.PointerProperty(type=GEOMESH_Props)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.geomesh

if __name__ == "main":
    register()