import rasterstats as rstats
import geopandas as gpd
import rasterio as rio 
from rasterio.mask import mask
import numpy as np
from util import export_to_tiff, write_rgb

class DataProcessor:
    
    def __init__(self, measurement, result_callback=None):
        self.red_file = measurement.red_path
        self.nir_file = measurement.nir_path
        self.title = measurement.title
        self.id = measurement.id
        self.cloudcover = measurement.cloudcover
        self.gjson = measurement.geojson_path
        self.result_callback = result_callback

        self.red_channel = measurement.red_path
        self.green_channel = measurement.green_path
        self.blue_channel = measurement.blue_path
    

    def format_measurement_results(self, res):
        result = res[0]['properties']
        veg_count = result['count']
        poly_count = veg_count + result['nodata']
        cov_percentage = veg_count * 100 / poly_count
        ret = {
            'abs_veg_cover': veg_count,
            'title': self.title,
            'id':self.id,
            'veg_cover_percentage': cov_percentage,
            'cloudcover': self.cloudcover,
            'img_link': '/static/img/{}.jp2'.format(self.title),
            'tiff_link': '/static/tiff/{}.tiff'.format(self.title)
        }
        return ret


    def process_data(self, df):
        nodata = -127
        with rio.open(self.red_file) as red, rio.open(self.nir_file) as nir:

            crs = red.crs.to_dict()
            # Reprojecting a featurecollection results in a weird
            # struct, the values of which are in an OrderedDict
            # or something. 
            # if this collection is guaranteed to contain one Feature,
            # indexing into it is simplest.
            shapes = gpd.read_file(self.gjson).to_crs(crs)
            shapefile = shapes.values.tolist()[0]

            crop = lambda img: mask(img, shapes.geometry, crop=True)
            red_cropped, red_transform = crop(red)
            nir_cropped, nir_transform = crop(nir)
            b4 = red_cropped[0]
            b8 = nir_cropped[0]
            np.seterr(divide='ignore', invalid='ignore')
            ndvi = (b8.astype(float) - b4.astype(float)) / (b8 + b4)
            ndvi_bi = ndvi
            ndvi_bi[np.where(ndvi_bi >= 0.20)] = 1
            ndvi_bi[np.where(ndvi_bi < 0.20)] = nodata

            result = rstats.zonal_stats(
                            vectors=shapefile[0],
                            raster=ndvi_bi,
                            stats=['count', 'nodata'],
                            geojson_out=True,
                            affine=red_transform,
                            nodata=nodata,
                            all_touched=True
                    )

            
            results = self.format_measurement_results(result)
            
            if self.result_callback is not None:
                self.result_callback(ndvi_bi, results, red.profile)


