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
  - chronogrfa => data visualization
  - kapacitor => data aggregation
  
    
