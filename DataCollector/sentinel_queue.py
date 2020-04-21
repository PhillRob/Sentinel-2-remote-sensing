from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from db_connection import DBClient
from zipfile import ZipFile
import os
from glob import glob

class SentinelClient:
    def __init__(
            self, 
            user=os.environ.get('SENTINEL_USER'),
            password=os.environ.get('SENTINEL_PASS'),
            url=os.environ.get('SENTINEL_URL'),
            footprint_path='sample-polygone.geojson'
            ):
        self.__user = user if user is not None else self.__get_default('user')
        self.__passwd = password if password is not None eeeelse self. 
        self.__url = url
        self.__footprint_path = footprint_path
        self.__api = SentinelAPI(
                self.__user, 
                self.__passwd, 
                self.__url
        )
        self.__dbclient = DBClient()
        self.__footprint = geojson_to_wkt(read_geojson(self.__footprint_path))
        self.__measurements = None
        self.__processing_thread = None
    
    
    def __get_default(self, var: str):
        return os.environ.get("SENTINEL_{}".format(var.upper))

    
    def fetch_measurements(self):
        tmp = self.__api.to_dataframe(self.__api.query(
                self.__footprint, 
                platformname='Sentinel-2',
                cloudcoverpercentage=(0,10),
                processinglevel='Level-1C'
        )).sort_values(['ingestiondate'], ascending=[False])
        # get rid of measurements already in influx
        self.__measurements = tmp[
            tmp.apply(
                lambda x: not self.__dbclient.measurement_exists(x.index), 
                axis=1
            )
        ]


    def __cleanup(self, title):
        zip_path = '{}.zip'.format(title)
        os.remove(zip_path)
        dirs = [ name for name in os.listdir('.') if os.path.isdir(os.path.join('.', name)) ]
        
        for i in dirs:
            os.rmdir(i)


    def __download_measurement(self, title, index):
        zip_name = '{}.zip'.format(title)
        self.__api.download_all(index) 
        with ZipFile(zip_name) as f:
            f.extractall('tmp')

    
    def __sen2cor_process(self, title):
        cmd = "L2A_Process --resolution 10 ./tmp/{title}.SAFE".format(title=title)
        os.system(cmd)
        # Ugly hack for the title, will fix
        output_name_constant = title[38:44]+ title[10:26]
        red_file = "".join(glob("**/*{out_name}_B04_10m.jp2".format(out_name=output_name_constant), recursive=True))
        nir_file = "".join(glob("**/*{out_name}_B08_10m.jp2".format(out_name=output_name_constant), recursive=True))
        
        return rif_file, nir_file 


    def __process_last_measurement(self):
        record = self.__measurements.head(1) 
        title = record.title[0]
        self.__download_measurement(title, record.index)
        red, nir = self.__sen2cor_process(title)
         
        self.__cleanup(title)


    def start_processing(self):
        pass

