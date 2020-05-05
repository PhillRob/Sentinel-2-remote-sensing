from datetime import datetime, timedelta
import os
import rasterio


def export_to_tiff(path, tite, tiff):
    out_path = '{path}/{title}.tiff'.format(title=title, path=path)
    with rasterio.Env():
        profile.update(
            dtype=rasterio.int8,
            count=1,
            driver='GTiff'
	)
        with rasterio.open(out_path, 'w', **profile) as dst:
            dst.write(tiff.astype(rasterio.int8), 1)


def last_2_weeks():
    return create_timeframe()


def create_timeframe(timeframe = timedelta(weeks=2)):
    start = datetime.now() - timeframe
    now = datetime.now()
    return start, now
