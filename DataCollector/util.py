from datetime import datetime, timedelta
import os
import rasterio 
from rasterio.mask import mask


def write_rgb(measurement, out_tiff):
    with rasterio.open(measurement.b2) as blue, \
        rasterio.open(measurement.b3) as green, \
        rasterio.open(measurement.red_path) as red:
        with rasterio.open(
                out_tiff, 
                'w',
                driver='Gtiff', 
                width=red.width, 
                height=red.height, 
                count=3,
                crs=red.crs,
                transform=red.transform, 
                dtype=red.dtypes[0]
            ) as rgb:
                rgb.write(blue.read(1),1) 
                rgb.write(green.read(1),2) 
                rgb.write(red.read(1),3) 


def export_to_tiff(path, title, tiff, profile):
    out_path = '{path}/{title}.tiff'.format(title=title, path=path)
    with rasterio.Env():
        profile.update(
            dtype=rasterio.int8,
            count=1,
            driver='GTiff'
	)
        with rasterio.open(out_path, 'w', **profile) as dst:
            dst.write(tiff.astype(rasterio.int8), 1)

    return out_path


def last_2_weeks():
    return create_timeframe()


def create_timeframe(timeframe = timedelta(weeks=2)):
    start = datetime.now() - timeframe
    now = datetime.now()
    return start, now
