from pandemic.movement import nudge, times_of_day
from pandemic.city import home_and_work_locations
from pandemic.conventions import INFECTED, VULNERABLE, POSITIVE, STATE_DESCRIPTIONS, SYMPTOMATIC, DECEASED
from pandemic.compliance import destinations
from pandemic.movement import evolve_positions, newly_exposed
from pandemic.health import contact_progression, individual_progression
from pandemic.plotting import plot_points
from collections import Counter
from pprint import  pprint
import numpy as np
import time

def simulate(params, plt=None, plot_hourly=None, xlabel=None ):

    if plot_hourly is None:
        plot_hourly = params['geometry']['n']<50000  # Hack, remove

    # Initialize a city's geography and its denizens
    num, num_initially_infected = int(params['geometry']['n']),int(params['geometry']['i'])
    num_times_of_day = int(params['motion']['t'])
    precision  = int(params['geometry']['p'])
    home, work = home_and_work_locations(geometry_params=params['geometry'],num=num)
    positions  = nudge(home,w=0.05*params['motion']['w'])
    status     = np.random.permutation([INFECTED]*num_initially_infected +[VULNERABLE]*(num-num_initially_infected))
    day_fraction = 1.0/num_times_of_day

    # Population drifts to work and back, incurring viral load based on proximity to others who are infected
    day = 0
    while any( s in [ INFECTED, POSITIVE, SYMPTOMATIC ] for s in status ):
        day = day+1
        for step_no, time_of_day in enumerate(times_of_day(num_times_of_day)):
            stationary = [ s in [DECEASED, POSITIVE] for s in status ]
            attractors = destinations(status, time_of_day, home, work)
            positions  = evolve_positions(positions=positions, motion_params=params['motion'], attractors=attractors,
                                         day_fraction=day_fraction, stationary=stationary )
            exposed = newly_exposed(positions=positions, status=status, precision=precision)
            status = contact_progression(status=status, health_params=params['health'], exposed=exposed)
            status = individual_progression(status, health_params=params['health'], day_fraction=day_fraction)

            if plt and ( plot_hourly or step_no % 12==0):
                plt.clf()
                plot_points(plt=plt, positions=positions, status=status, title="Day "+str(day)+':'+str(time_of_day*num_times_of_day))
                b = params['geometry']['b']
                plt.axis([-b,b,-b,b])
                if xlabel:
                    plt.xlabel(xlabel)
                plt.show(block=False)
                plt.pause(0.01)
            pprint(Counter([list(STATE_DESCRIPTIONS.values())[s] for s in status]))



