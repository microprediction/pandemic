# A community experiment to build a surrogate model

import requests, math, copy, json, random
from collections import Counter
from pandemic.conventions import STATES
from pandemic.zcurves import to_zcurve, from_zcurve
from pandemic.example_parameters import BASELINES
from pandemic.conventions import params_to_vector, vector_to_params, CATEGORIES, STATE_DESCRIPTIONS
from pandemic.zcurves import to_zcurve
from pandemic.simulation import simulate
import numpy as np
from pprint import pprint

#-------------------------
#   Free parameters
#-------------------------

FREE_PARAMS = {'motion':{'w'},
               'geometry':{'c'},
               'health':{'sp'}}
FREE_DIM = len(FREE_PARAMS)

def free_param_percentiles(params,baseline='large_town'):
    """ Takes parameter set and returns a vector of numbers between 0 and 1 """
    free = list()
    for c in CATEGORIES:
        for ky in FREE_PARAMS[c]:
            raw = params[c][ky]
            default = BASELINES[baseline][c][ky]
            ratio   = raw / default
            prctl = 1. / (1. + math.exp(-ratio)/math.exp(-1))
            free.append(prctl)
    return free

PARAMS_SCALE = 1000 * 1000 * 1000 * 1000 * 1000
def cube_to_int(v):
    """ z=curve """
    assert 2<=len(v)<=3
    assert [ abs(v_)<=1.0 for v_ in v]
    z = to_zcurve(v)
    return int(PARAMS_SCALE * z)

def int_to_cube(h, dim):
    """ Map integer back to the cube"""
    z = h / PARAMS_SCALE
    v = from_zcurve(z,dim)
    return v

DAY_SCALE = 10000
def days_to_int(day, day_fraction):
    return int(DAY_SCALE*(day+day_fraction))

def int_to_days(key):
    return int(key) / DAY_SCALE


#----------------------------------------
#   Examples of reporting callbacks
#----------------------------------------

def health_metric(status, **ignore_other_kwargs):
    counts = Counter(status)
    return [ counts[k] for k,_ in enumerate(STATES) ]

def random_modification_ratio():
    return math.exp(np.random.randn())

def random_modification(params):
    for c, prms in FREE_PARAMS.items():
        for prm in list(prms):
            params[c][prm] = random_modification_ratio()*params[c][prm]
    return params

#----------------------------------------
#   Client for www.swarmprediction.com
#----------------------------------------

class Surrogate():

    def __init__(self, baseline='town', url='https://www.swarmprediction.com/', callback_metric=health_metric, plt=None, params=None):
        self.baseurl  = url+baseline
        self.baseline = baseline
        self.callback_metric = callback_metric
        self.params   = params or random_modification( copy.deepcopy( BASELINES[baseline] ) )
        self.WIDTH    = 2+len(str(DAY_SCALE))+len(str(PARAMS_SCALE))
        self.plt      = plt
        self.history  = list()
        self.quietude = 10           # How often to pprint results

    def to_key(self, day, day_fraction ):
        return str(self.to_int(day=day, day_fraction=day_fraction, params=self.params)).zfill(self.WIDTH)

    def to_int(self, day, day_fraction, params ):
        """ Map (time,params) to integer """
        v = free_param_percentiles(params)
        params_as_int = cube_to_int(v)
        time_as_int = days_to_int(day=day, day_fraction=day_fraction)
        return time_as_int*PARAMS_SCALE + params_as_int

    def from_int(self,time_and_params):
        """ Map integer back to (time,params) """
        elapsed      = int( math.floor( time_and_params / PARAMS_SCALE ) )
        params_as_int = time_and_params % PARAMS_SCALE
        params = int_to_cube(params_as_int,dim=FREE_DIM)
        return elapsed, params

    def run(self):
        simulate(params=self.params,callback=self.callback,plot_hourly=False,plt=self.plt,xlabel="Sending results to www.swarmprediction.com. Thanks!")

    def callback(self, day, day_fraction, status, positions, home, work, **ignore_other_kwargs):
        metrics = self.callback_metric(status=status)
        ky      = self.to_key(day=day, day_fraction=day_fraction)
        res     = self.post(key=ky, metrics=metrics)
        self.history.append(ky)
        if random.choice(range(self.quietude))==0:
            pprint({"key":ky,"result":res,"metrics":metrics})

    def post(self, key, metrics):
        """ The server stores results in a REDIS sorted set, where the score is an embedding of the parameters
            from R^3 into R via a Morton curve. Similar simulations with nearby parameters can be retrieved if
            they are close on the space filling curve ... which is often though not always the case. We *may* introduce
            redundancy into the embeddings to improve this somewhat.
        """
        res = requests.post(self.baseurl +'/' + key, data={'metrics':json.dumps(metrics)})
        return res.status_code if res.status_code not in [200,201] else res.json()

    def get(self,key):
        res = requests.get(url=self.baseurl + '/' + str(key) )
        return res.status_code if res.status_code not in [200,201] else res.json()

    def get_nearby(self, day, day_fraction, params, precision=6):
        """ Retrieves scenarios which used similar parameters and the same exact time step """
        key  = self.to_key(day=day, day_fraction=day_fraction, params=params)
        res  = requests.get_nearby(url=self.baseurl+'/' + str(key), data={'precision':precision})
        return res.json() if res.status_code==200 else res.status_code

    def get_timeseries(self):
        """ Retrieve metrics from database """
        num_times_of_day = self.params['motion']['t']
        from pandemic.movement import times_of_day
        finished = False
        day = 0
        history = list()
        times   = list()
        while not finished:
            day = day + 1
            for step_no, day_fraction in enumerate(times_of_day(num_times_of_day)):
                key     = self.to_key(day=day, day_fraction=day_fraction)
                metrics = self.get(key=key)
                if metrics:
                    times.append(day+day_fraction)
                    history.append(metrics)
                else:
                    finished = True
        return times, metrics

    def plot_metrics(self,plt):
        times, metrics = self.get_timeseries()
        plt.plot( zip(*metrics) )
        plt.legend( list(STATE_DESCRIPTIONS.keys() ) )
        plt.show(block=False)
        plt.pause(5)

def surrogate(plot=True):
    if plot:
        try:
            import matplotlib.pyplot as plt
        except:
            plt = None
    else:
        plt=None
    while True:
        s = Surrogate(plt=plt)
        pprint(s.params)
        s.run()
        s.plot_metrics()

if __name__=="__main__":
    surrogate()
