from sentinelsat import read_geojson, geojson_to_wkt
import os
import shutil
import glob 
from zipfile import ZipFile

class SentinelMeasurement:
    def __init__(self, api, dataframe, geojson_path, autofetch=False):
        self.title = dataframe.title[0]
        self.id = dataframe.uuid[0]
        self.time = dataframe.endposition[0]
        self.index = dataframe.index
        self.cloudcover = dataframe.cloudcoverpercentage[0]
        self.geojson_path = geojson_path
        self.output_dir = '{}_unzipped'.format(self.title)
        self.zip_path = '{}.zip'.format(self.title)
        self.__api__ = api
        if autofetch:
            self.fetch()


    def is_download_done(self):
        return os.path.isdir(self.output_dir)


    def fetch(self):
        self.__download_and_unzip__()
        self.__find_output_files__()


    def __find_output_files__(self):

        regex_format = self.output_dir + '/**/*_B0{nr}_10m.jp2'
        # print(regex_format)
        
        red_file = "".join(
                glob.glob(regex_format.format(nr=4), recursive=True))
        nir_file = "".join(
                glob.glob(regex_format.format(nr=8), recursive=True))
        self.red_path = red_file
        self.nir_path = nir_file

    def __download_and_unzip__(self):
        if(self.is_download_done()):
            return
        
        self.__api__.download_all(self.index)
        with ZipFile(self.zip_path) as zf:
            zf.extractall(self.output_dir)
       
        os.remove(self.zip_path)


    def cleanup(self):
        if self.is_download_done():
            shutil.rmtree(self.output_dir)
