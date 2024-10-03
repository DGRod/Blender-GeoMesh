# Blender-GeoMesh

A custom addon for Blender to import GIS raster elevation data and model it as a 3D surface. Currently supports TIFF and XYZ files.


## Features
- Import raster data from TIFF or XYZ files into Blender
- Model elevation data as a 3D surface
- Adjust the model's scale and vertical exaggeration in real-time
- Apply multiresolution modifier to add detail


## Installation
1. Latest release available on [GitHub](https://github.com/DGRod/Blender-GeoMesh)
2. If using Windows, install the appropriate GDAL wheel for Python [here](https://github.com/cgohlke/geospatial-wheels/releases)
3. Install necessary dependencies:
`pip install requirements.txt`
4. In Blender, go to `Edit > Preferences > Add-ons` and click `Install from Disk` under the drop-down menu
5. Select the downloaded .zip file and enable the addon in the preferences


## Usage
1. In the 3D Viewport, click on the `GeoMesh` panel
2. Click on `Import Raster` and select a TIFF or XYZ file
3. The raster data will be modeled as a 3D surface
4. Use the settings in the panel to adjust the model's properties


## Resources
- [Blender](https://www.blender.org/)
- [QGIS](https://qgis.org/)
- [GDAL](https://gdal.org/en/latest/#)
