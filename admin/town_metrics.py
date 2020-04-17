
from pandemic.config_private import REDIS_CONFIG
from pprint import pprint
import json
from pandemic.surrogate import Surrogate

# Use a set of params we know is populated
PARAMS = {'geometry': {'b': 25,
              'c': 0.4012592037488107,
              'e': 0.05,
              'h': 2.5,
              'i': 50,
              'n': 40000,
              'p': 6,
              'r': 0.04,
              's': 0.25},
 'health': {'id': 0.00035714285714285714,
            'ip': 0.025,
            'ir': 0.07107142857142858,
            'is': 0.1,
            'pd': 0.0014285714285714286,
            'pr': 0.06857142857142857,
            'sd': 0.002142857142857143,
            'sp': 0.4193638077407048,
            'sr': 0.06928571428571428,
            'vi': 1.0},
 'motion': {'k': 3.0, 't': 24, 'w': 0.8362853086535382}}


if __name__=="__main__":
     s = Surrogate(params=PARAMS)
     times, metrics = s.get_timeseries()
     pprint(metrics)

