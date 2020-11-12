from pandemic.config_private import REDIS_CONFIG
from pprint import pprint
import json

if __name__=="__main__":
    import redis
    key = '123414'
    baseline ='testing'
    jmetrics = json.dumps({"whatever":17})

    r = redis.Redis(**REDIS_CONFIG)
    r.delete(baseline + '::zset')
    r.delete((baseline + '::hash'))
    res1  = r.zadd(name=baseline + '::zset', mapping={str(jmetrics): int(key)})
    res2  = r.hset(name=baseline + '::hash', key=key, value=jmetrics )
    data  = r.hgetall(name=baseline + '::hash')
    data1 = json.loads( r.hget(name=baseline+ '::hash',key=key) )


