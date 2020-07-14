
from pandemic.config_private import REDIS_CONFIG
from pandemic.conventions import STATE_DESCRIPTIONS
from pprint import pprint
import json
import math
import pandas as pd

from pandemic.surrogate import Surrogate, PARAMS_SCALE, int_to_days


if __name__=="__main__":
    import redis
    r = redis.Redis(**REDIS_CONFIG)
    data = r.hgetall(name='city::hash')

    surrogate = Surrogate(baseline='city')

    # Get all valid parameter keys that have at least 150 days
    all_params = set()
    all_keys   = set()
    ddata = list()
    for s,v in data.items():
        i = int(s)
        vdata = [v_/800000 for v_ in json.loads(v)]
        all_keys.add(i)
        params_as_int = i % PARAMS_SCALE
        elapsed = float(s[:8])/10000
        record = {'key':i,'params':params_as_int,'elapsed':elapsed,'reverse_key':params_as_int*1000+elapsed}
        for name, val in zip(STATE_DESCRIPTIONS.values(),vdata):
            record.update({name:val})
        ddata.append( record )

    sdata = sorted(ddata,key=lambda x: x['reverse_key'] )
    df = pd.DataFrame.from_records(sdata)
    g = df.groupby(by='params').count().sort_values(by='key')
    valid = list( g[g['key'] > 150].index.values )
    print(len(valid))
    valid_row = [k in valid for k in df['params'].values]
    df1 = df.loc[valid_row,:]
    df1.sort_values(by=['params','elapsed'],inplace=True)
    df1.drop(columns=['key','params','elapsed','reverse_key'],inplace=True)
    df1.to_csv('dump.csv')

