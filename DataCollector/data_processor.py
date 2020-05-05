import rasterstats as rstats
import rasterio as rio 
import numpy as np

class DataProcessor:
    
    def __init__(self, measurement, result_callback=None):
        self.red_file = measurement.red_path
        self.nir_file = measurement.nir_path
        self.title = measurement.title
        self.cloudcover = measurement.cloudcover
        self.gjson = measurement.geojson_path
        self.result_callback = result_callback
    

    def format_measurement_results(self, res):
        result = res[0]['properties']
        veg_count = result['count']
        poly_count = veg_count + result['nodata']
        cov_percentage = poly_count * 100 / veg_count 
        ret = {
            'abs_veg_cover': veg_count,
            'veg_cover_percentage': cov_percentage,
            'cloudcover': self.cloudcover,
            'img_link': '/static/img/{}.jp2'.format(self.title),
            'tiff_link': '/static/tiff/{}.tiff'.format(self.title)
        }
        return ret


    def process_data(self, df):
        with rio.open(self.red_file) as red, rio.open(self.nir_file) as nir:
            b4 = red.readd(1)
            b8 = nir.read(1)
            np.seterr(divide='ignore', invalid='ignore')
            ndvi = (b8.astype(float) - b4.astype(float)) / (
                    b8.astype(float) + b4.astype(float))  # check if the second needs to be float!!!
            ndvi_bi = ndvi
            white = len(np.where(ndvi > .2)[1])
            ndvi_bi[np.where(ndvi_bi >= 0.20)] = 1
            ndvi_bi[np.where(ndvi_bi < 0.20)] = nodata

            crs = red.crs.to_dict()
            shapefile = gpd.read_file(geojson_path).to_crs(crs).values.tolist()[0]
            # veg_coverage_abs, veg_cover_rel, cloudcover, img_link, tiff_link
            result = zonal_stats(
                            vectors=shapefile,
                            raster=ndvi_bi,
                            stats=['count', 'nodata'],
                            geojson_out=True,
                            affine=red.transform,
                            nodata=nodata,
                            all_touched=True
                    )


            results = self.format_measurement_results(result)
            if self.result_callback is not None:
                self.result_callback(ndvi_bi, results)



