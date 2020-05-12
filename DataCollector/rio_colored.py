import geopandas as gpd
import rasterio as rio
from rasterio.mask import mask
import numpy as np
import os

class RGBImage:
    def __init__(self, measurement, base_path='.', autogen=False):
        self.red_channel = measurement.red_path
        self.green_channel = measurement.green_path
        self.blue_channel = measurement.blue_path
        self.geojson_path = measurement.geojson_path
        self.tmp_tiff_path = '{}/{}_full.tiff'.format(base_path, measurement.title)
        self.cropped_path = '{}/{}_cropped.tiff'.format(base_path, measurement.title)
        self.result_path = '{}/{}_result.tiff'.format(base_path, measurement.title)
        self.generated = False
        if autogen: 
            self.__gen_all__()


    def __gen_full_tiff__(self):
        with rio.open(self.red_channel) as red, \
             rio.open(self.green_channel) as green, \
             rio.open(self.blue_channel) as blue:
            crs = red.crs.to_dict()
            self.shapes = gpd.read_file(self.geojson_path).to_crs(crs)
            self.shapefile = self.shapes.values.tolist()[0]

            with rio.open(
                    self.tmp_tiff_path,
                    'w',
                    driver='GTiff', 
                    nodata=None, 
                    width=red.width, 
                    height=red.height,
                    count=3,
                    crs=red.crs,
                    transform=red.transform, 
                    dtype=red.dtypes[0], 
                    photometric="RGB") as rgb:
                rgb.write(red.read(1)*8, 1)   
                rgb.write(green.read(1)*8, 2) 
                rgb.write(blue.read(1)*8, 3)  

    

    def __gen_cropped_tiff__(self):
        with rio.open(self.tmp_tiff_path) as src:
            out_image, out_transform = mask(src, self.shapes.geometry,crop=True)
            out_meta = src.meta.copy()
            out_meta.update({"driver": "GTiff",
                         "height": out_image.shape[1],
                         "width": out_image.shape[2],
                         "transform": out_transform,
                         "photometric":"RGB"
                         })
            # print(out_meta)
        
        with rio.open(self.cropped_path, "w", **out_meta) as dest:
            dest.write(out_image)


    def __gen_all__(self):
        self.__gen_full_tiff__()
        self.__gen_cropped_tiff__()
        self.generated = True

    
    def generate_output(self, overlay=None):
        if not self.generated:
            self.__gen_all__()

        if overlay is None:
            self.result_path = self.cropped_path

    def cleanup(self):
        os.remove(self.tmp_tiff_path)

