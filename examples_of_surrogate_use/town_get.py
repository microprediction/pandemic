from pprint import pprint
from pandemic.surrogate import Surrogate


s = Surrogate(baseline='town')
metrics = s.get(key='00010000117159480338133') # <--- Put your key here or it won't work.
pprint(metrics)