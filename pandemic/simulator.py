from pandemic.example_parameters import BASELINES, TOWN
from pandemic.conventions import parameter_category, DECEASED, POSITIVE, VULNERABLE, INFECTED
from pandemic.movement import evolve_positions, newly_exposed
from pandemic.health import contact_progression, individual_progression
from pandemic.compliance import destinations
from pandemic.city import home_and_work_locations
from pandemic.conventions import INFECTED, VULNERABLE
import numpy as np
from pandemic.movement import times_of_day, nudge
from pandemic.plotting import plot_callback
from pandemic.metrics import status_counts, cases_and_deaths
from pprint import pprint
from copy import deepcopy


# A more object oriented simulator

class BaseSimulator(object):

    def __init__(self, params=None, baseline=None, data=None ):
        self.params = params or (BASELINES[baseline] if BASELINES else None) or TOWN
        self.state  = {'positions':None,'status':None,'attractors':None,'home':None,'work':None,'clock':{'day':0,'time_of_day':0}}
        self.data   = data or {'daily':list(),'step':list(),'final':None} # All metrics and other outputs
        if self.state['home'] is None or self.state['work'] is None:
            self.state['home'], self.state['work'] = home_and_work_locations(geometry_params=self.params['geometry'], num=self.params['geometry']['n'])
        if self.state['status'] is None:
            self.state['status'] = np.random.permutation([INFECTED] * self.params['geometry']['i'] + [VULNERABLE] * (self.params['geometry']['n'] - self.params['geometry']['i']) )


    # -----------------------------------------------------------
    # Manage metric generation
    # -----------------------------------------------------------

    def daily_metrics(self):
        return status_counts(self.state['status'])

    # -----------------------------------------------------------
    # Manage interventions and logging by overriding one of these
    # -----------------------------------------------------------

    def midnight_callback(self):
        pass

    def noon_callback(self):
        pass

    def morning_callback(self):
        """ Called at 6 am """
        self.state['attractors'] = destinations(status=self.state['status'], day_fraction=0.25, home_locations=self.state['home'], work_locations=self.state['work'])

    def evening_callback(self):
        """ Called at 6 pm """
        self.state['attractors'] = destinations(status=self.state['status'], day_fraction=0.75, home_locations=self.state['home'], work_locations=self.state['work'])

    def step_callback(self):
        """ Called after every time step """
        pass

    def quarterly_callback(self):
        """ Called four times a day """
        pass

    def end_of_day_callback(self):
        """ Called at midnight but not on first day """
        pass

    def end_of_week_callback(self):
        pass

    def start_of_run_callback(self):
        pass

    def end_of_run_callback(self):
        pass

    def stopping_criteria(self):
        return self.state['clock']['day']>20 and not any( s==INFECTED for s in self.state['status'] )

    # -----------------------------------------------------------
    #   Evolution
    # -----------------------------------------------------------

    def _ensure_state(self):
        """ Ensure """
        if self.state['home'] is None or self.state['work'] is None:
            self.state['home'], self.state['work'] = home_and_work_locations(geometry_params=self.params['geometry'],
                                                                             num=self.params['geometry']['n'])
        if self.state['positions'] is None:
            self.state['positions'] = nudge(self.state['home'], w=0.05 * self.params['motion']['w'])
        if self.state['attractors'] is None:
            self.state['attractors'] = destinations(status=self.state['status'], day_fraction=0.75,
                                                    home_locations=self.state['home'],
                                                    work_locations=self.state['work'])

    def run(self):
        self._ensure_state()
        self.start_of_run_callback()
        while not self.stopping_criteria():
            self.day()
            self.end_of_day_callback()
            self.state['clock']['day'] = self.state['clock']['day'] + 1
            print(self.state['clock']['day'])
            self.end_of_run_callback()
            self.data['daily'].append(self.daily_metrics())
            if self.state['clock']['day'] % 7 ==0:
                self.end_of_week_callback()
        self.data['final']=self.daily_metrics()

    def _intraday_callback(self):
        return [self.midnight_callback, self.morning_callback, self.noon_callback, self.evening_callback ]

    def day(self):
        """ Step through a day """
        num_times_of_day = int(self.params['motion']['t'])
        assert num_times_of_day % 4 ==0,'Must be multiple of four'
        day_times = times_of_day(num_times_of_day)
        num_quarter = int(num_times_of_day/4)
        for quarter in range(4):
            self._intraday_callback()[quarter]()
            quarter_times = day_times[quarter*num_quarter:(quarter+1)*num_quarter]
            for tod in quarter_times:
                self.state['clock']['time_of_day']=tod
                self.step()
                self.step_callback()
            self.quarterly_callback()


    def step(self):
        time_step = 1./self.params['motion']['t']
        precision = self.params['geometry']['p']
        stationary = [s in [DECEASED, POSITIVE] for s in self.state['status']]
        self.state['positions'] = evolve_positions(positions=self.state['positions'], motion_params=self.params['motion'], attractors=self.state['attractors'],
                                              time_step=time_step, stationary=stationary)
        exposed = newly_exposed(positions=self.state['positions'], status=self.state['status'], precision=precision)
        self.state['status'] = contact_progression(status=self.state['status'], health_params=self.params['health'], exposed=exposed)
        self.state['status'] = individual_progression(self.state['status'], health_params=self.params['health'], day_fraction=time_step)



    # -----------------------------------------------------------
    #       Convenience
    # -----------------------------------------------------------

    def set_param(self, parameter, value, category=None):
        """ e.g.  set_param(parameter='k',value=4.5) """
        category = category or parameter_category(parameter)
        self.params[category][parameter] = value

    def __repr__(self):
        return {'params':self.params,'state':self.state,'data':self.data}




# -----------------------------------------------------------
#       Some examples of deriving...
# -----------------------------------------------------------


class MatplotLibSimulator(BaseSimulator):

    def __init__(self, params=None, baseline=None):
        super().__init__(params=params, baseline=baseline)
        import matplotlib.pyplot as plt
        self.plt = plt
        self.xlabel = 'Ornstein-Uhlenbeck pandemic simulation'

    def quarterly_callback(self):
        super().quarterly_callback()
        plot_callback(positions=self.state['positions'], status=self.state['status'], params=self.params,
                      day=self.state['clock']['day'], day_fraction=self.state['clock']['time_of_day'], home=self.state['home'], work=self.state['work'], plt=self.plt, step_no=0, hourly=True,
                      xlabel=self.xlabel)


class CasesSimulator(BaseSimulator):
    # Report something else in the metrics history
    # As an alternative you can just set the daily_metrics method to a new function

    def __init__(self, params=None, baseline=None):
        super().__init__(params=params, baseline=baseline)

    def daily_metrics(self):
        return status_counts(self.state['status'])


class LockdownSimulator(MatplotLibSimulator):

    def __init__(self, params=None, baseline=None, infection_threshold=0.01, patience=14):
        super().__init__(params=params, baseline=baseline)
        self.state['locked'] = False
        self.patience = patience or 14    # Maximum length of lockdown
        self.infection_threshold = infection_threshold

    def lockdown(self):
        self.pre_lockdown_work = deepcopy(self.state['work'])
        self.state['work'] = deepcopy(self.state['home'])
        self.state['locked']=True
        self.state['lockdown_day'] = self.state['clock']['day']
        self.xlabel = 'LOCKDOWN'

    def openup(self):
        self.state['work'] = deepcopy(self.pre_lockdown_work)
        self.state['locked']=False
        self.xlabel = 'LOCKDOWN REVOKED'

    def end_of_week_callback(self):
        super().end_of_week_callback()
        infection_level = np.mean( [ s==INFECTED for s in self.state['status']] )
        if not(self.state['locked']) and infection_level>self.infection_threshold:
            self.lockdown()
        if self.state['locked'] and ( infection_level<self.infection_threshold or (self.state['clock']['day']>self.state['lockdown_day']+self.patience)):
            self.openup()




if __name__=="__main__":
    simulator = LockdownSimulator(baseline='town')
    simulator.set_param(parameter='vi',value=0.5)
    simulator.run()
    pprint(simulator.daily_metrics())  # Barf final count