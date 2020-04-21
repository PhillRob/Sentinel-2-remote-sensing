from datetime import datetime, timedelta
import os


def last_2_weeks():
    return create_timeframe()


def create_timeframe(timeframe = timedelta(weeks=2)):
    start = datetime.now() - timeframe
    now = datetime.now()
    return start, now
