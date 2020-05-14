import matplotlib.pyplot as plt
from pandemic.simulation import simulate
from pandemic.example_parameters import LARGE_TOWN
from pandemic.conventions import unflatten, flatten, STATE_DESCRIPTIONS, DECEASED
from metrics import cases_and_deaths
from pandemic.example_parameters import BASELINES
import numpy as np
import math, pprint
from copy import deepcopy


BUDGET = 1500


class Evaluator():

    """ Early stopping objective function """

    def __init__(self, params, data, lockdown_start, plt=None):
        self.params = params
        self.data   = data   # Vector of empirical data
        self.time_history = list()
        self.metric_history = list()
        self.plt = plt
        self.threshold_discrepancy = 2.0
        self.lockdown_start = lockdown_start
        if plt is not None:
            self.fig, self.axs = plt.subplots(nrows=2,ncols=2)

    def objective(self):
        """ Try to get to the end ! """
        simulate(params=self.params, callback=self.callback, hourly=False, plt=self.plt, stopping_i=1)
        return len(self.metric_history)+10*(self.threshold_discrepancy-self.running_discrepancy)

    def discrepancy_metric(self, d1, d2):
        return abs(math.log(d1[0]+20)-math.log(d2[0]+20)) + 15*abs(math.log(d1[1]+10)-math.log(d2[1]+10))

    def discrepancy(self):
        scores = list()
        for offset in range(5):
            offset_metric = [[0,0]]*offset + self.metric_history
            scores.append(  np.mean([self.discrepancy_metric(m, d) for m, d in zip(offset_metric, self.data)]) )
        return min(scores)

    def callback(self, day, day_fraction, status, positions, home, work, plt, **ignore_other_kwargs):
        """ This gets called after each computation cycle (see pandemic/simulation.py) """

        if day_fraction==0:
            n = len(self.metric_history)
            if n>1:
                print( list(zip( self.metric_history[n-1], self.data[n-1] )) )
            metrics = cases_and_deaths(status=status)
            self.metric_history.append(metrics)
            self.time_history.append(day+day_fraction)
            self.running_discrepancy = self.discrepancy()
            import pprint
            print('discrepancy='+str(self.running_discrepancy))
            print('day '+str(day))
            from pandemic.conventions import INFECTED
            print(str(sum([s==INFECTED for s in status]))+' infected.')
            if self.running_discrepancy >self.threshold_discrepancy or day>len(self.data):
                return {'kill':True} # kill signal
            if day==self.lockdown_start:
                return {"lockdown":True}


def evaluate_model(assignments, data, lockdown_start, plt=None ):
    """
    :param assignments:      flattenned parameters
    :param lagged_metrics:   [ [ ], [] ]  daily series of metrics
    :return:
    """
    # Assignment is:
    #       'i': 50, 'r': 0.04 'e': 0.05, 'c': 0.5,
    #       'w': 1.0

    FIXED_PARAMS = {
        'geometry': {'b': 50, 's': 0.25,  'p': 6},
        'motion': {'t': 24, 'w': 1.0},
        'health': {'vi':1.0,'ip':0.025,'id':0.005/14,'sr':0.97/14,'pr':0.96/14}
    }
    assignments.update( flatten(FIXED_PARAMS) )

    dr = assignments['death_reporting']
    cr = assignments['case_reporting']
    ecr = assignments['early_case_reporting']
    lag = assignments['lag']
    data  = [ (d[0]/ecr,d[1]/dr) for d in data[:14] ] + [ (d[0]/cr,d[1]/dr) for d in data[14:] ]

    data = data[lag:]
    del assignments['lag']
    del assignments['early_case_reporting']
    del assignments['death_reporting']
    del assignments['case_reporting']
    params = unflatten(assignments)
    ev     = Evaluator(params=params, data=data, plt=plt, lockdown_start=lockdown_start )
    score  = ev.objective()
    return score


def evaluate_county(assignments, county='New York City', lockdown_start=23):
    from empirical.sources import get_nyt
    cases  = get_nyt()
    county = cases.loc[cases['county'] == county, :]
    SCALE  = 0.1
    data = list(zip([SCALE * c for c in county['cases'].values], [SCALE * d for d in county['deaths'].values]))
    return evaluate_model(assignments=assignments, data=data, plt=None, lockdown_start=lockdown_start )

PARAMS = [ {'name':'geometry_i',     'type':'int',     'bounds':{'min':3,     'max':8} },
           {'name':'geometry_n',     'type':'int',     'bounds':{'min':30000,  'max':50000} },
           {'name':'geometry_r',     'type':'double',  'bounds':{'min':0.05,  'max':0.15} },
           {'name':'geometry_e',     'type': 'double', 'bounds':{'min':0.02,  'max':0.1}},
           {'name':'geometry_c',     'type': 'double', 'bounds':{'min': 0.65,  'max':0.95}},
           {'name':'geometry_h',     'type':'double',  'bounds':{'min':2,      'max':5}},
           {'name':'motion_w',       'type': 'double', 'bounds':{'min': 1.3,  'max':3.5}},
           {'name':'motion_k',       'type':'double',  'bounds':{'min':5    , 'max':12}},
           {'name':'health_ip',      'type': 'double', 'bounds':{'min': 0.01, 'max':0.05}},
           {'name':'health_sp',      'type': 'double', 'bounds':{'min': 0.025, 'max': 0.25}},
           {'name':'health_pd',      'type': 'double', 'bounds':{'min':0.001, 'max': 0.003}},
           {'name':'health_sd',     'type': 'double', 'bounds': {'min': 0.001, 'max': 0.003}},
           {'name':'health_ir',      'type': 'double', 'bounds':{'min':0.06, 'max': 0.11}},
           {'name':'health_is',      'type': 'double', 'bounds':{'min':0.05 , 'max': 0.15}},
           {'name':'early_case_reporting', 'type': 'double', 'bounds': {'min': 0.02, 'max': 0.2}},
           {'name':'case_reporting', 'type':'double',  'bounds':{'min':0.2,  'max':1.0}},
           {'name':'death_reporting','type': 'double', 'bounds':{'min':0.5,   'max':1.0}},
           {'name':'lag',            'type': 'int',    'bounds': {'min': 7, 'max': 14}}
           ]

from config_private import SIG_KEY

def example_evaluation():
    assignments = flatten(deepcopy(LARGE_TOWN))
    assignments['geometry_i'] = 10
    assignments['geometry_r'] = 1.5 * assignments['geometry_r']
    assignments['geometry_b'] = 50
    score = evaluate_county(assignments)
    print(score)

METRICS = [ {'name':'evaluate_county','objective':'maximize'} ]
from sigopt import Connection

class Optimizer():

    def __init__(self, experiment_id=None ):
        self.conn = Connection(client_token=SIG_KEY)
        if experiment_id is None:
            experiment = self.conn.experiments().create(name='new_york_city', parameters=PARAMS, metrics=METRICS, observation_budget=BUDGET, project='pandemic')
            self.experiment_id = experiment.id
        else:
            self.experiment_id = experiment_id

    def optimize(self):
        experiment = self.conn.experiments(self.experiment_id).fetch()
        while experiment.progress.observation_count < experiment.observation_budget:
            suggestion = self.conn.experiments(experiment.id).suggestions().create()
            value = evaluate_county(assignments=suggestion.assignments)
            self.conn.experiments(experiment.id).observations().create(
                suggestion=suggestion.id,
                value=value,
            )
            # Update the experiment object
            experiment = self.conn.experiments(experiment.id).fetch()

            # Fetch the best configuration and explore your experiment
        all_best_assignments = self.conn.experiments(experiment.id).best_assignments().fetch()
        # Returns a list of dict-like Observation objects
        best = all_best_assignments.data[0].assignments
        return best

if __name__=="__main__":
    opt = Optimizer(experiment_id=199263)
    opt.optimize()
