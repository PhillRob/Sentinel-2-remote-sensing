#!/usr/bin/env python3
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from db_connection import DBClient
import dotenv
import os
from pprint import pprint as pp

dotenv.load_dotenv()

if __name__ == '__main__':
    api = SentinelAPI(os.environ.get('SENTINEL_USER'), os.environ.get('SENTINEL_PASS'), os.environ.get('SENTINEL_URL'))

    # I left the poly-gone pun in for good measure
    footprint = geojson_to_wkt(read_geojson('sample-polygone.geojson'))
    products = api.query(footprint, platformname='Sentinel-2',
                         cloudcoverpercentage=(0, 10), processinglevel='Level-1C')

    products_df = api.to_dataframe(products)

    # sort for most recent and lowest cloud cover
    products_df_sorted = products_df.sort_values(['ingestiondate'], ascending=[False])

    dbclient = DBClient()
    products_filtered = products_df_sorted[products_df_sorted.apply(lambda x: not dbclient.measurement_exists(x.index), axis=1)]

    # GeoJSON FeatureCollection containing footprints and metadata of the scenes
    geojson_products = api.to_geojson(products)

    # GeoPandas GeoDataFrame with the metadata of the scenes and the footprints as geometries
    geodata_products = api.to_geodataframe(products)

    pp(products_filtered.head(1))

    pass
