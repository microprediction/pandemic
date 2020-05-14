from pandemic.movement import nudge, times_of_day
from pandemic.city import home_and_work_locations
from pandemic.conventions import INFECTED, VULNERABLE, POSITIVE, STATE_DESCRIPTIONS, SYMPTOMATIC, DECEASED
from pandemic.compliance import destinations
from pandemic.movement import evolve_positions, newly_exposed
from pandemic.health import contact_progression, individual_progression
from pandemic.plotting import plot_points, plot_callback
from collections import Counter
from pprint import  pprint
import numpy as np



def simulate(params, plt=None, hourly=None, xlabel=None, callback=plot_callback, home=None, work=None, positions=None, stopping_i=None, stopping_t=None):
    """ OU Pandemic simulation
    :param params:       dict of dict as per pandemic.conventions
    :param plt:          Handle to matplotlib plot
    :param hourly:  Bool        Set False to speed up, True to see commuting
    :param xlabel:       str         Label for plot
    :param callback:     Any function taking home, work, day, params, positions, status (e.g. for plotting, saving etc)
    :return: None        Use the callback
    """
    if stopping_i is None:
        import math
        stopping_i = int(math.ceil(0.7 * params['geometry']['i']))
    if hourly is None:
        hourly = params['geometry']['n'] < 50000  # Hack, remove
    if stopping_t is None:
        stopping_t = 150

    # Initialize a city's geography and its denizens
    num, num_initially_infected = int(params['geometry']['n']),int(params['geometry']['i'])
    num_times_of_day = int(params['motion']['t'])
    precision  = int(params['geometry']['p'])
    if home is None or work is None:
        home, work = home_and_work_locations(geometry_params=params['geometry'],num=num)
    if positions is None:
        positions  = nudge(home,w=0.05*params['motion']['w'])
    status     = np.random.permutation([INFECTED]*num_initially_infected +[VULNERABLE]*(num-num_initially_infected))
    time_step  = 1.0/num_times_of_day

    day = 0
    killed = False
    while sum( s in [ INFECTED ] for s in status )>=stopping_i and day<stopping_t and not killed:
        day = day+1
        for step_no, day_fraction in enumerate(times_of_day(num_times_of_day)):
            stationary = [ s in [DECEASED, POSITIVE] for s in status ]
            attractors = destinations(status, day_fraction, home, work)
            positions  = evolve_positions(positions=positions, motion_params=params['motion'], attractors=attractors,
                                          time_step=time_step , stationary=stationary )
            exposed = newly_exposed(positions=positions, status=status, precision=precision)
            status = contact_progression(status=status, health_params=params['health'], exposed=exposed)
            status = individual_progression(status, health_params=params['health'], day_fraction=time_step )

            if callback:
                signal = callback(day=day, day_fraction=day_fraction, home=home, work=work, positions=positions, status=status, params=params, step_no=step_no, hourly=hourly, plt=plt, xlabel=xlabel)
                if signal is not None:
                    if 'kill' in signal:
                        killed = True
                    if 'lockdown' in signal:
                        work = [ h for h in home ]
                    if 'params' in signal:
                        params.update(signal['params'])
    pprint(Counter([list(STATE_DESCRIPTIONS.values())[s] for s in status]))

