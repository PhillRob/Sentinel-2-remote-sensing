import os
from influxdb import InfluxDBClient


class DBClient:
    def __init__(self):
        self.__addr = os.environ.get('INFLUX_ADDRESS')
        self.__port = os.environ.get('INFLUX_PORT')
        self.__user = os.environ.get('INFLUX_USER')
        self.__passwd = os.environ.get('INFLUX_PASS')
        self.__dbname = 'sentinel_data'
        self.client = InfluxDBClient(
            self.__addr,
            self.__port,
            self.__user,
            self.__passwd,
            self.__dbname
        )
        dbnames = [x['name'] for x in self.client.get_list_database()]
        if self.__dbname not in dbnames:
            self.client.create_database(self.__dbname)

        pass

    def push_measurement(self, measurement: dict):

        pass

    def measurement_exists(self, id: str):
        query = self.client.query('SELECT index FROM satellite_measurements WHERE id=$id', bind_params={'id': id})
        return len(query.items) > 0
