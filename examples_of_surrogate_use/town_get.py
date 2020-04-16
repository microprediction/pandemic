from pprint import pprint
from pandemic.surrogate import Surrogate


s = Surrogate()
metrics = s.get(key='00014166361513445490518')
pprint(metrics)