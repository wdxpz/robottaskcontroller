from datetime import datetime

def dt2timestamp(dt):
    timestamp = (dt - datetime(1970, 1, 1)).total_seconds()
    return timestamp