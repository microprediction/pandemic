
from pandemic.config_private import REDIS_CONFIG
from pprint import pprint
import json

if __name__=="__main__":
    import redis
    r = redis.Redis(**REDIS_CONFIG)
    key     = '00021250616501801290085'
    min_key = '00021250016501801290085'
    max_key = '00021250916501801290085'
    data = r.zrangebyscore(name='town::zset',min=min_key, max=max_key, withscores=True)
    pprint(data)
