#!/usr/bin/env python3
from sentinel_queue import SentinelQueue
from time import sleep
import os


if __name__ == '__main__':
    import dotenv
    dotenv.load_dotenv()
    nginx_tiff_dir = '/static_content/tiff'
    nginx_img_dir = '/static_content/images'
    if not os.path.isdir(nginx_tiff_dir):
        os.mkdir(nginx_tiff_dir)
    if not os.path.isdir(nginx_img_dir):
        os.mkdir(nginx_img_dir)
    
    period = 60*int(os.environ.get('FREQUENCY_HOURS'))
    while True: 
        try:
            queue = SentinelQueue()
            queue.process_all_data()
        except Exception as e:
            print(str(e))
            exit(1)
        sleep(period) 
