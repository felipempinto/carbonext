import ee
import geemap
import geopandas as gpd

########################################################
file = "deforestation/selected1.shp"
year = 2021
########################################################

# Authenticate and initialize Earth Engine
ee.Authenticate()  # Uncomment this if you haven't authenticated yet
ee.Initialize()

# Define your region of interest
gdf = gpd.read_file(file)
geometry = gdf.geometry.iloc[0]
geometry_type = geometry.geom_type

print(f"Geometry Type: {geometry_type}")

if geometry_type == 'Polygon':
    acre_coordinates = geometry.__geo_interface__['coordinates']
    acre_region = ee.Geometry.Polygon(acre_coordinates)

elif geometry_type == 'MultiPolygon':
    polygons = [poly.__geo_interface__['coordinates'] for poly in geometry.geoms]
    acre_region = ee.Geometry.MultiPolygon(polygons)

else:
    raise ValueError("Unsupported geometry type")

# Define the Sentinel-2 image collection
sentinel2_collection = ee.ImageCollection('COPERNICUS/S2') \
    .filterBounds(acre_region) \
    .filterDate(f'{year}-01-01', f'{year}-12-31') \
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 1))

# Select the median image from the collection (or any other processing you need)
sentinel2_image = sentinel2_collection.median()

# Define visualization parameters (modify as needed)
vis_params = {
    'bands': ['B4', 'B3', 'B2'],  # Red, Green, Blue
    'min': 0,
    'max': 3000,
    'gamma': 1.4
}

# Export the image to Google Drive
task = ee.batch.Export.image.toDrive(
    image=sentinel2_image,
    description='Sentinel2_Export',
    folder='EarthEngineImages',
    fileNamePrefix=f'sentinel2_image_{year}',
    scale=10,  # Sentinel-2 has a 10m resolution for these bands
    region=acre_region.getInfo()['coordinates'],
    crs='EPSG:4326'
)

task.start()

# Print task status
print("Export task started. Check your Google Drive for the output.")
