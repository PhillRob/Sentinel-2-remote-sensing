import concurrent.futures
from multiprocessing import Pool, Lock
import os
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from db_connection import DBClient
from data_processor import DataProcessor
from sentinel_measurement import SentinelMeasurement
from util import export_to_tiff


class SentinelQueue:

    def process_all_data(self):
        self.__threadpool__.apply(self.__process_one_product__)


    def __init__(self, geojson_path='sample-polygone.geojson', max_threads=4):
        # private
        self.__lock__ = Lock()
        # self.__dbconn__ = DBClient() 
        self.__api__ = self.__get_sentinel_api__()
        self.__geojson_path__ = geojson_path
        self.__footprint__ = geojson_to_wkt(read_geojson(geojson_path))
        self.__threadpool__ = Pool(max_threads)
        # public
        self.max_threads = max_threads
        self.products = self.__fetch_measurements__()


    def __get_env_var__(self, varname):
        return os.environ.get('SENTINEL_{}'.format(varname.upper()))

    
    def __save_result__(self, measurement, tiff, result):
        export_to_tiff(path='/static/tiff', title=measurement.title, tiff=tiff) 
        with self.__lock__.acquire():
            self.__dbconn__.push_measurement(measurement.time, result)


    def __process_one_product__(self):
        with self.__lock__.acquire():
            df = self.products.head(1)
            self.products.drop([0])
        measurement = SentinelMeasurement(
                self.__api__, 
                self.__geojson_path__,
                True
                )
        dp = DataProcessor(
                measurement, 
                lambda tiff,result: self.__save_result__(measurement, tiff, result))
        dp.process_data(df)


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
        )).sort_values(['ingestiondate'], ascending=[False])
        # get rid of measurements already in influx
        self.measurements = tmp[
            tmp.apply(
                lambda x: not self.__dbconn__.measurement_exists(x.index),
		axis=1
            )
        ]


