import numpy as np
import math
from geohash import encode
from pandemic.conventions import INFECTED, SYMPTOMATIC, POSITIVE, VULNERABLE


MOTION_DESCRIPTIONS    = {'T':'Number of time steps in a day','k':'fractional distance moved towards attractor per day (kappa)','s':'standard deviation per day (brownian motion term)'}

def times_of_day(n):
    return [ 1.0*k/n for k in range(n) ]

def nudge(positions,w):
    return [ (pos[0] + w*np.random.randn(),pos[1] + w*np.random.randn()) for pos in positions ]

def random_location(r):
    return (np.random.uniform(-r,r),np.random.uniform(-r,r))

def evolve_positions( positions, motion_params, attractors, day_fraction, stationary ):
    """ OU process time increment """
    W     = motion_params['w']*math.sqrt(day_fraction)/math.sqrt(2)
    kappa = motion_params['k']*day_fraction
    return[ p if st else (p[0]+W*np.random.randn()+kappa*(a[0]-p[0]),p[1]+W*np.random.randn()+kappa*(a[1]-p[1])) for p,a,st in zip(positions, attractors, stationary) ]

def newly_exposed(positions, status, precision):
    """
         :precision  int      Geohash precision.
         :returns  [ bool ]
    """
    SICK = set([INFECTED,SYMPTOMATIC])  # Add POSITIVE here if you have less faith in humanity
    infected_locations = set( [ encode(pos[0],pos[1],precision=precision) for pos,s in zip(positions,status) if s in SICK  ] )
    return [ s==VULNERABLE and encode(pos[0],pos[1],precision=precision) in infected_locations for s,pos in zip(status,positions) ]


