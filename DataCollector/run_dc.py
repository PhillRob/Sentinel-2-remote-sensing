#!/usr/bin/env python3
from sentinel_queue import SentinelQueue


if __name__ == '__main__':
    import dotenv
    dotenv.load_dotenv()
    queue = SentinelQueue()
    queue.process_all_data()

