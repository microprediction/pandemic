
from pandemic.config_private import REDIS_CONFIG
from pprint import pprint
import json

if __name__=="__main__":
    import redis
    r = redis.Redis(**REDIS_CONFIG)
    r.delete('town::hash')
    r.delete('town::zset')


