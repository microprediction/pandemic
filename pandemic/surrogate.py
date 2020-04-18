# A community experiment to build a surrogate model

import requests, math, copy, json, random
from collections import Counter
from pandemic.conventions import STATES
from pandemic.zcurves import to_zcurve, from_zcurve
from pandemic.example_parameters import BASELINES
from pandemic.conventions import params_to_vector, vector_to_params, CATEGORIES, STATE_DESCRIPTIONS
from pandemic.zcurves import to_zcurve
from pandemic.simulation import simulate
from pandemic.plotting import plot_points
import numpy as np
from pprint import pprint
import matplotlib.pyplot as plt

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

    def __init__(self, baseline, url='https://www.swarmprediction.com/metrics', callback_metric=health_metric, plt=None, params=None, quietude=24):
        self.baseurl  = url
        self.baseline = baseline
        self.callback_metric = callback_metric
        self.params   = params or random_modification( copy.deepcopy( BASELINES[baseline] ) )
        self.WIDTH    = 2+len(str(DAY_SCALE))+len(str(PARAMS_SCALE))
        self.time_history = list()
        self.key_history  = list()
        self.metric_history = list()
        self.quietude = quietude
        self.plt = plt
        if plt is not None:
            self.fig, self.axs = plt.subplots(nrows=2,ncols=2)

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

    def callback(self, day, day_fraction, status, positions, home, work, plt, **ignore_other_kwargs):
        """ This gets called after each computation cycle (see pandemic/simulation.py) """
        if day_fraction==0:
            metrics = self.callback_metric(status=status)
            ky      = self.to_key(day=day, day_fraction=day_fraction)
            res     = self.post(key=ky, metrics=metrics)
            self.key_history.append(ky)
            self.metric_history.append(metrics)
            self.time_history.append(day+day_fraction)
            if random.choice(range(self.quietude)) == 0:
                if self.plt is not None:
                    self.plot(plt=plt,positions=positions,status=status)
                pprint({"key":ky,"day":str(day+day_fraction),"result":res,"retrieve":self.baseurl.replace('metrics',self.baseline)+'/'+ky})
                print(' ',flush=True)

    def post(self, key, metrics):
        """ The server stores results in a REDIS sorted set, where the score is an embedding of the parameters
            from R^3 into R via a Morton curve. Similar simulations with nearby parameters can be retrieved if
            they are close on the space filling curve ... which is often though not always the case. We *may* introduce
            redundancy into the embeddings to improve this somewhat.
        """
        res = requests.post(self.baseurl +'/' + key, data={'baseline':self.baseline,'metrics':json.dumps(metrics)})
        return res.status_code if res.status_code not in [200,201] else res.json()

    def get(self,key):
        res = requests.get(url=self.baseurl + '/' + str(key), params={'baseline':self.baseline} )
        return res.status_code if res.status_code not in [200,201] else res.json()

    def get_nearby(self, day, day_fraction, params, precision=6):
        """ Retrieves scenarios which used similar parameters and the same exact time step """
        key  = self.to_key(day=day, day_fraction=day_fraction, params=params)
        res  = requests.patch(url=self.baseurl+'/' + str(key), data={'precision':precision,'baseline':self.baseline})
        return res.json() if res.status_code==200 else res.status_code

    def plot(self,plt,positions,status):

        # Population plot
        self.axs[0][0].clear()
        plot_points( plt=self.axs[0][0], positions=positions, status=status )
        self.axs[0][0].figure

        # Metrics plots, regular and logarithmic
        for k in range(2):
            self.axs[1][k].clear()
            self.plot_metrics(plt=self.axs[1][k], logarithmic=k)
            self.axs[1][k].figure

        # Rates of change
        self.axs[0][1].clear()
        self.plot_metrics(plt=self.axs[0][1], logarithmic=False, differences=True)
        self.axs[0][1].figure


        plt.show(block=False)
        plt.pause(0.01)

    def plot_metrics(self, plt, logarithmic, differences=False):
        metrics = list(zip(*self.metric_history))[1:]
        if len(metrics[0])>3:
            for m in metrics:
                if differences:
                    plt.plot(self.time_history[1:], list(np.diff(m)))
                    plt.set_ylabel('Daily change')
                else:
                    plt.plot(self.time_history,m)
                    plt.set_ylabel('Cumulative')
            if logarithmic:
                plt.set_yscale('log')
            labels = list(STATE_DESCRIPTIONS.values())[1:]
            if differences:
                labels = [ 'net newly '+lb for lb in labels ]
            plt.legend(labels)
            plt.set_xlabel('Days since first '+str(self.params['geometry']['i'])+' infections.')

def surrogate(baseline='city',plot=True,quietude=5):
    print('Starting pandemic simulation',flush=True)
    if plot:
        try:
            import matplotlib.pyplot as plt
        except:
            plt = None
            print("Plotting does not seem to be working, but calculations will proceed")
    else:
        plt=None

    s = Surrogate(plt=plt,baseline=baseline,quietude=quietude)
    pprint(s.params)
    s.run()
    if s.plt is not None:
        s.plt.close()
    while True:
        s = Surrogate(plt=None,baseline=baseline,quietude=quietude)
        pprint(s.params)
        s.run()

if __name__=="__main__":
    surrogate(baseline='town',quietude=1)
