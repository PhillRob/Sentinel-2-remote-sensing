# Sentinel Data Collector

## Container setup

### Volumes
  - influxdb
  - shared image volume

### Containers
  - dc-python 
    - data collector, fetches Sentinel measurements and processes them
    - entrypoint: run_dc.py
    - mounts shared img vol
  - dc-nginx
    - hosts static images
    - acts as a proxy for chronograf
    - mounts shared img vol
  - influxdb => TSDB, mounts influxdb
  - chronograf => data visualization
  
 ### dc-python 
  - SentinelQueue (file: DataCollector/sentinel_queue.py) 
    - owns a DBConnection 
    - owns a SentinelAPI
    - Creates Measurmenets
    - Spawns DataProcessors for said measurements
  - DBConnection (file: DataCollector/db_connection.py)
    - Abstraction layer in front of InfluxDB
    - Can verify, if a measurement is unique
    - Can push a measurement to database
  - DataProcessor (file: DataCollector/data_processor.py)
    1. Crops the maps to the specified polygon 
    2. Processes the rasters using RasterIO and RasterStats
    3. Produces a raster, in which two distinct values denote vegetation or the lack thereof
    4. Calls a specifiad callback
  - RGBImage (file: DataCollector/rio_colored.py)
    - utiliy class for exporting tiff's 
