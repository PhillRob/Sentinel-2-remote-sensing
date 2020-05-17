import concurrent.futures
from multiprocessing import Lock
from multiprocessing.pool import ThreadPool
import os
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from db_connection import DBClient
from data_processor import DataProcessor
from sentinel_measurement import SentinelMeasurement
from rio_colored import RGBImage
from util import export_to_tiff


class SentinelQueue:

    def process_all_data(self):
        while not self.products.empty:
            self.__threadpool__.apply(self.__process_one_product__)


    def __init__(self, geojson_path='sample-polygone.geojson', max_threads=4):
        # private
        self.__lock__ = Lock()
        self.__dbconn__ = DBClient() 
        self.__api__ = self.__get_sentinel_api__()
        self.__geojson_path__ = geojson_path
        self.__footprint__ = geojson_to_wkt(read_geojson(geojson_path))
        self.__threadpool__ = ThreadPool(max_threads)
        self.__img_path__ = self.__get_env_var__('img_path')
        self.__tiff_path__ = self.__get_env_var__('tiff_path')
        # public
        self.max_threads = max_threads
        self.__fetch_measurements__()
        # print("Measurement count = {}".format(self.products))


    def __get_env_var__(self, varname):
        return os.environ.get('SENTINEL_{}'.format(varname.upper()))

    
    def __save_result__(self, measurement, tiff, result, profile):
        overlay_path = export_to_tiff(path=self.__tiff_path__, title=measurement.title, tiff=tiff, profile=profile) 
        
        cropped = RGBImage(measurement, base_path=self.__img_path__ ,autogen=True, overlay_path=overlay_path)
        result['tiff_link'] = overlay_path
        result['img_link'] = cropped.result_path
        self.__dbconn__.push_measurement(measurement.time, result)
        cropped.cleanup()
        measurement.cleanup()


    def __process_one_product__(self):
        df = self.products.head(1)
        measurement = SentinelMeasurement(
                api=self.__api__, 
                geojson_path=self.__geojson_path__,
                dataframe=df,
                autofetch=True
                )
        dp = DataProcessor(
                measurement, 
                lambda tiff,result, profile: self.__save_result__(measurement, tiff, result, profile))
        dp.process_data(df)
        self.products = self.products.iloc[1:]
        products_left = len(self.products.index)
        print("{} measurements are left".format(products_left))


    def __get_sentinel_api__(self):
        sentinel_vars = ['user', 'pass', 'url']
        tmp = dict([(x, self.__get_env_var__(x)) for x in sentinel_vars])
        return SentinelAPI(tmp['user'], tmp['pass'], tmp['url'])


    def __fetch_measurements__(self):
        tmp = self.__api__.to_dataframe(self.__api__.query(
                self.__footprint__,
                platformname='Sentinel-2',
                cloudcoverpercentage=(0,10),
                processinglevel='Level-2A'
        )).sort_values(['ingestiondate'], ascending=[True])
        # get rid of measurements already in influx
        self.products = tmp[
            tmp.apply(
                lambda x: not self.__dbconn__.measurement_exists(x),
		axis=1
            )
        ]
        print("Measurements to be processed: {}".format(len(self.products.index)))


