from pprint import pprint
from pandemic.surrogate import Surrogate


s = Surrogate(baseline='city')
metrics = s.get(key='00020000110618823310936') # <--- Put your key here or it won't work.
pprint(metrics)