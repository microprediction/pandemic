from pandemic.example_parameters import SMALL_CITY, TOWN
from pandemic.simulation import simulate
import matplotlib.pyplot as plt
from copy import deepcopy
import numpy as np
import math

def equal_spaced_homes(b,num):
    num1 = int(math.sqrt(num))
    return [ (x,y) for x in np.linspace(-b,b,num1) for y in np.linspace(-b,b,num1) ]



if __name__=="__main__":
    params = deepcopy(TOWN)
    num = 10000
    params['geometry']['b']=5.0
    b = params['geometry']['b']
    params['motion']['t']=48
    params['geometry']['c']=0.0   # Nobody commutes
    params['health']['vi'] = 50.0 # Collision -> infection
    home = equal_spaced_homes(b,num)
    work = deepcopy(home)
    params['geometry']['n'] = len(home)
    pos = deepcopy(home)
    simulate(params=params, home=home, work=work, positions=pos, plt=plt)

