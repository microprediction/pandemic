
from pandemic.config_private import REDIS_CONFIG
from pprint import pprint
import json

if __name__=="__main__":
    import redis
    r = redis.Redis(**REDIS_CONFIG)
    key = '00021250616501801290085'
    data = r.hgetall(name='town::hash')
    pprint(data)
