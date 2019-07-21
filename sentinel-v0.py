from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date
import rasterio
#from rasterio.plot import show
#import plotly.graph_objs as go
#import plotly as py
import pandas as pd
import zipfile
import os
import gmplot
import glob
import numpy as np
from rasterstats import zonal_stats
#import gdal
#from osgeo import gdal  # If GDAL doesn't recognize jp2 format, check version</pre>
import matplotlib.pyplot as plt
import geopandas as gpd
#import pysal as ps
#from pysal.contrib.viz import mapping as maps


# connect to the API
api = SentinelAPI('phillr', 'testme2019', 'https://scihub.copernicus.eu/dhus')

# search by polygon, time, and SciHub query keywords
footprint = geojson_to_wkt(read_geojson('South-v0.geojson'))
products = api.query(footprint, date=('20190601', date(2019, 7, 30)), platformname='Sentinel-2', cloudcoverpercentage=(0, 10), processinglevel='Level-1C')

# todo check for processed data
len(products)

# convert to Pandas DataFrame
products_df = api.to_dataframe(products)

# sort for most recent and lowest cloud cover
products_df_sorted = products_df.sort_values(['ingestiondate','cloudcoverpercentage'], ascending=[True, True])

test = products_df_sorted.head(1)
test['cloudcoverpercentage']
test['ingestiondate']
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
# todo: needs loop to run through the data sets
directory_to_extract_to = "unzip"
zip = zipfile.ZipFile(str(test.title[0])+'.zip')
zip.extractall(directory_to_extract_to)
zip.close()

# todo: only process certain bands
#os.system("mkdir /Users/philipp/Projects/PycharmProjects/sentinel/unzip/" + str(test.title[1]) + '.SAFE/NDVIBANDS')
#os.system('cp /Users/philipp/Projects/PycharmProjects/sentinel/unzip/'+str(test.title[1])+'.SAFE/GRANULE'+str(test.index[1])+'IMG_DATA'+ str(test.title[1])[-22:]/Users/philipp/Projects/PycharmProjects/sentinel/unzip/"+str(test.title[1])+'.SAFE/NDVIBANDS')


# atmospheric correction using Sen2Cor
cmd = '/Applications/Sens2Cor/bin/L2A_Process --resolution 10 '+'/Users/philipp/Projects/PycharmProjects/RS/unzip/'+ str(test.title[0])+'.SAFE'
os.system(cmd)

# read bands
red_file = "".join(glob.glob('**/*'+str(test.title[0])[38:44]+str(test.title[0])[10:26]+'_B04_10m.jp2', recursive=True))
nir_file = "".join(glob.glob('**/*'+str(test.title[0])[38:44]+str(test.title[0])[10:26]+'_B08_10m.jp2', recursive=True))

with rasterio.open(red_file) as src:
	b4 = src.read(1)
	b4_meta = src.profile
dst = rasterio.open(red_file)

with rasterio.open(nir_file) as src:
	b8 = src.read(1)
	b8_meta = src.profile

# ignore division by 0 and calc
np.seterr(divide='ignore', invalid='ignore')
ndvi = (b8.astype(float) - b4.astype(float)) / (b8.astype(float) + b4.astype(float))  # check if the second needs to be float!!!
#ndvi = (b8.astype(float) - b4.astype(float)) / (b8 + b4)  # check if the second needs to be float!!!

# set tjhreshold
ndvi_bi = ndvi
ndvi_bi[np.where(ndvi_bi >= 0.2)] = 1
ndvi_bi[np.where(ndvi_bi < 0.2)] = -999999999999

# plot
plt.imshow(ndvi_bi)
plt.show()

plt.imshow(ndvi)
plt.show()

# load shapefile
shapefile = gpd.read_file("Wadi-v1.shp")

shapefile.plot()
plt.show()

# zonal stats for rel veg cover
result = zonal_stats(vectors=shapefile, raster=ndvi_bi, stats=('count', 'nodata'), geojson_out=True, affine=dst.transform, nodata=-999999999999)

# convert to data frame
vc = []
nd = []
area = []
df = pd.DataFrame({'area': [], 'vc': [], 'nd': []})

# appending rows
for data in result:
	print(data['properties']['Des'], ((data['properties']['count']) / (data['properties']['count'] + data['properties']['nodata'])*100))
	area.append((data['properties']['Des']))

	#centroid
	# polystring = str(data['geometry']['coordinates'])
	# polystring = polystring.replace('), (', ',')
	# polystring = polystring.replace(', ', ' ')
	# polystring = polystring.replace('[(', '')
	# polystring = polystring.replace(')]', '')
	# data['polystring'] = polystring
	#
	# polystringf = shapely.wkt.loads('POLYGON '+ polystring)
	# data['centroid'] = polystringf.centroid
	#
	# centroid = polystringf.centroid
	#
	# data['centroidx'] = centroid.x
	# data['centroidy'] = centroid.y

	vc.append((data['properties']['count']) / (data['properties']['count'] + data['properties']['nodata']) * 100)
	nd.append(data['properties']['nodata'])
	r = (area, vc, nd)
	#result['vc'] = vc

df = pd.DataFrame(r)
df = df.T
df.sort_values(by=[1], inplace=True)

# write to disk
# Register GDAL format drivers and configuration options with a
# context manager.
with rasterio.Env():

	# Write an array as a raster band to a new 8-bit file. For
	# the new file's profile, we start with the profile of the source
	profile = src.profile

	# And then change the band count to 1, set the
	# dtype to uint8, and specify LZW compression.
	profile.update(
		dtype=rasterio.int8,
		count=1,
		driver='GTiff')

	with rasterio.open('NDVI_'+str(test.title[0])+'.tif', 'w', **profile) as dst:
		dst.write(ndvi_bi.astype(rasterio.int8), 1)

# At the end of the ``with rasterio.Env()`` block, context
# manager exits and all drivers are de-registered.

#todo: loop through features and plot polygons on raster

import fiona
import rasterio.plot
import matplotlib as mpl
from descartes import PolygonPatch
from shapely.geometry import shape
src = rasterio.open('NDVI_'+str(test.title[0])+'.tif')


with fiona.open("Wadi-v1.shp", "r") as shapefile:
	features = [feature["geometry"] for feature in shapefile]
	bounds = [shape(feature['geometry']).bounds for feature in shapefile]


rasterio.plot.show((src, 1, nodata= '-999999999999'))
ax = mpl.pyplot.gca()

patches = [PolygonPatch(feature) for feature in features]
ax.add_collection(mpl.collections.PatchCollection(patches))

patches = [PolygonPatch(feature, edgecolor="red", facecolor="none", linewidth=1) for feature in features]

ax.add_collection(mpl.collections.PatchCollection(patches, match_original=True))

#todo change detection
