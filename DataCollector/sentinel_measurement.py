from sentinelsat import read_geojson, geojson_to_wkt
import os
from zipfile import ZipFile

class SentinelMeasurement:
    def __init__(self, api, dataframe, geojson_path, autofetch=False):
        self.title = dataframe.title[0]
        self.time = dataframe.endposition[0]
        self.index = dataframe.index
        self.cloudcover = dataframe.cloudcoverpercentage[0]
        self.geojson_path = geojson_path
        self.output_dir = '{}_unzipped'.format(self.title)
        self.zip_path = '{}.zip'.format(self.title)
        self.__api__ = api
        if autofetch:
            fetch()


    def is_download_done(self):
        return os.path.isdir(self.output_dir)


    def fetch(self):
        self.__download_and_unzip__()
   

    def __download_and_unzip__(self):
        if(self.is_download_done()):
            return
        
        self.__api__.download_all(self.index)
        with ZipFile(self.zip_path) as zf:
            zf.extractall(self.output_dir)
       
        os.remove(self.zip_path)


    def __del__(self):
        if self.is_download_done():
            os.rmdir(output_dir)
