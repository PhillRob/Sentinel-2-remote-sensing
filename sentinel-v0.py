from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date
import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import plotly as py
import pandas as pd
import zipfile
import os
import glob
import numpy as np
from rasterstats import zonal_stats
#import gdal
#from osgeo import gdal  # If GDAL doesn't recognize jp2 format, check version</pre>
import geopandas as gpd


# connect to the API
api = SentinelAPI('phillr', 'testme2019', 'https://scihub.copernicus.eu/dhus')

# search by polygon, time, and SciHub query keywords
footprint = geojson_to_wkt(read_geojson('map.geojson'))
products = api.query(footprint, date=('20190601', date(2019, 7, 30)), platformname='Sentinel-2', cloudcoverpercentage=(0, 10),processinglevel='Level-1C')

# todo check for processed data
len(products)

# convert to Pandas DataFrame
products_df = api.to_dataframe(products)
products_df_sorted = products_df.sort_values(['ingestiondate','cloudcoverpercentage'], ascending=[True, True])

test = products_df_sorted.head(2)
set(products_df['processinglevel'])

# GeoJSON FeatureCollection containing footprints and metadata of the scenes
geojson_products = api.to_geojson(products)

# GeoPandas GeoDataFrame with the metadata of the scenes and the footprints as geometries
geodata_products = api.to_geodataframe(products)

# plot product time vs cloudcover
# data = [go.Scatter(x=products_df_sorted.ingestiondate, y=products_df_sorted[['cloudcoverpercentage']])]
# py.plotly.iplot(data, filename = 'time-series-simple')

# download
api.download_all(test.index)

# unzip
# todo: needs loop

directory_to_extract_to = "unzip"
zip = zipfile.ZipFile(str(test.title[1])+'.zip')
zip.extractall(directory_to_extract_to)
zip.close()

# todo: only process certain bands
#os.system("mkdir /Users/philipp/Projects/PycharmProjects/sentinel/unzip/" + str(test.title[1]) + '.SAFE/NDVIBANDS')

# todo: delete files other than B03 and B04
#a=os.system("mv /Users/philipp/Projects/PycharmProjects/sentinel/unzip/" + str(test.title[1]) + '.SAFE/NDVIBANDS \;')


#os.system('cp /Users/philipp/Projects/PycharmProjects/sentinel/unzip/'+str(test.title[1])+'.SAFE/GRANULE'+str(test.index[1])+'IMG_DATA'+ str(test.title[1])[-22:]/Users/philipp/Projects/PycharmProjects/sentinel/unzip/"+str(test.title[1])+'.SAFE/NDVIBANDS')


# todo: atmospheric correction using Sen2Cor
cmd = '/Applications/Sens2Cor/bin/L2A_Process --resolution 10 '+'/Users/philipp/Projects/PycharmProjects/RS/unzip/'+ str(test.title[1])+'.SAFE'
os.system(cmd)



# Search directory for desired bands
red_file = "".join(glob.glob('**/*B04.jp2', recursive=True))
nir_file = "".join(glob.glob('**/*B08.jp2', recursive=True))

with rasterio.open(red_file) as src:
	b4 = src.read(1)
	sp =src.profile

dst = rasterio.open(red_file)

with rasterio.open(nir_file) as src:
	b8 = src.read(1)
type(b8)


# ignore division by 0 and calc
np.seterr(divide='ignore', invalid='ignore')
ndvi = (b8.astype(float) - b4.astype(float)) / (b8 + b4)


# set tjhreshold
ndvibi = ndvi
ndvibi[np.where(ndvibi>=0.2)] = 1
ndvibi[np.where(ndvibi<0.2)] = -999999999999
# plot
plt.imshow(ndvibi)
plt.show()

# load shapefile
shapefile = gpd.read_file("1435-center.shp")


result = zonal_stats(vectors = shapefile ,raster=ndvibi, stats='count', geojson_out = True,affine=dst.transform, nodata=-999999999999)

(result[0]['properties']['count']*100) / result[0]['properties']['SHAPE_Area']*100

chm_reclass[np.where((chm_array>0) & (chm_array<=20))] = 2 # 0m < CHM <= 20m - Class 2
chm_reclass[np.where((chm_array>20) & (chm_array<=40))] = 3 # 20m < CHM < 40m - Class 3
chm_reclass[np.where(chm_array>40)] = 4 # CHM > 40m - Class 4



# Take a spatial subset of the ndvi layer produced
ndvi_sub = ndvi[2000:3000, 2000:3000]

# Plot
plt.imshow(ndvi)
plt.show()


# Create output filename based on input name
outfile_name = red_file[0].split('_B')[0] + '_NDVI.tif'

x_pixels = ndvi2.shape[0]  # number of pixels in x
y_pixels = ndvi2.shape[1]  # number of pixels in y

# Set up output GeoTIFF
driver = gdal.GetDriverByName('GTiff')

# Create driver using output filename, x and y pixels, # of bands, and datatype
ndvi_data = driver.Create(outfile_name, x_pixels, y_pixels, 1, gdal.GDT_Float32)

# Set NDVI array as the 1 output raster band
ndvi_data.GetRasterBand(1).WriteArray(ndvi2)

# Setting up the coordinate reference system of the output GeoTIFF
geotrans = red_link.GetGeoTransform()  # Grab input GeoTranform information
proj = red_link.GetProjection()  # Grab projection information from input file

# now set GeoTransform parameters and projection on the output file
ndvi_data.SetGeoTransform(geotrans)
ndvi_data.SetProjection(proj)
ndvi_data.FlushCache()
ndvi_data = None
###############################################################################
< pre >





# Open the file:
raster = rasterio.open(b03)
show(raster)


