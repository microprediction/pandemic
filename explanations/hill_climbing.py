from ddeint import ddeint
import numpy as np
from math import exp, ceil
import matplotlib.pyplot as plt
import math




#----------------------------------------------------------------------------------------
#   Standalone compartmental model with delay DEs illustrating a vague physical analogy
#-----------------------------------------------------------------------------------------




def novel_collision_probability(dt, a):
    return (1 - exp(-a * dt)) / (a * dt) if dt*a > 1e-4 else 1.0


def mean_attenuation(infection_func, t, g, a):
    """ Crudely estimate the mean attenuation

        Given a history of infections up to time t, this function tries to estimate the mean probability of the next collision being novel
        It is consistent with a physical model where particles make normal jumps from equi-spaced home locations on the plane.
        There are probably better ways to implement the system

    """
    if t*a<0.01:
        return 1.0
    else:
        t_high        =  t
        t_low         =  0
        num_interp_points = 5+int(ceil(t/2))
        ts             = np.linspace(t_low, t_high, num_interp_points)
        dt             = ts[1]-ts[0]
        its            = [infection_func(t_) for t_ in ts]
        net_new_its    = np.diff( [0]+its )
        new_its        = [ max(0,net_new + g*dt*existing) for net_new,existing in zip(net_new_its,its) ]   # Estimate of how many are new, taking into account those recovering

        scaling_factor = max( new_its + [1e-4] )
        scaled_new_its = [ ni/scaling_factor for ni in new_its ]

        survival       = [exp(-g * (t - t_)) for t_ in ts]  # Odds that they are still infected
        weights        = [ survive*it_+1e-4 for survive,it_ in zip(survival,scaled_new_its) ]  # Weighted
        sum_w          = sum(weights)
        normalized     = [ w/sum_w for w in weights ]
        assert abs(sum(normalized)-1)<1e-6, 'not normalized'
        att            = [w * novel_collision_probability(dt=t - t_, a=a) for w, t_ in zip(normalized, ts)]
        attenuation    = sum(att)
        return attenuation

def model(Y, t, a, b, g ):
    """ SIR model with novelty attenuation """
    infection_func = lambda t: Y(t)[1]
    avg_attenuation = mean_attenuation(infection_func=infection_func,t=t,g=g,a=a)
    new_infections = Y(t)[0]*Y(t)[1]*(b*avg_attenuation)
    new_recoveries = Y(t)[1]*g
    attenuation_rate = (avg_attenuation-Y(t)[3])
    return [ -new_infections, new_infections-new_recoveries, new_recoveries, attenuation_rate ]


def values_before_zero(t):
    return [0.9999, 0.0001, 0.0, 1.0]

def moving_average(a, n=3) :
    ma = list()
    recent = list()
    for x in a:
        recent.append(x)
        if len(recent)>=n:
            recent.pop(0)
        ma.append(np.mean(recent))
    return ma


def hill(acceleration):
    """ Create a hill in such a way that something sliding up it might experience acceleration proportional
        to a supplied vector of accelerations.
    """
    suma     = sum(acceleration)    # Ball will stop at top
    if suma<0:
        acceleration = [-a for a in acceleration]
    v0     = sum(acceleration)
    y      = 0
    ys     = list()
    v      = v0
    xs     = list()
    x      = 0
    import math
    for a in acceleration:
        theta = math.asin(a)
        dy    = math.tan(theta)
        y     = y+dy
        ys.append(y)
        v     = v - a
        vx    = v*math.cos(a)
        x     = x + vx
        xs.append(x)

    return xs, ys




def make_hill(a,time_grid):
    " Solve DDE and plot a hill "
    b = 0.10+math.sqrt(0.02+math.pow(a,0.75))*0.135
    g = 0.06
    derivatives = lambda Y,t : model(Y,t,a,b,g)
    yy = ddeint(derivatives, values_before_zero, time_grid)
    infected    = yy.T[1]
    stopped = [ i< 0.5*infected[0] for i in infected ]
    if any(stopped):
        stop_ndx = stopped.index()
    else:
        stop_ndx = len(infected)-1
    infected = infected[:stop_ndx]

    position = [ math.log(i) for i in infected ]
    velocity = moving_average( np.gradient( position ), 10 )
    acceleration = moving_average( np.gradient( velocity ), 10 )
    hill_x,hill_y = hill(acceleration)
    return hill_x, hill_y



#----------------------------------------------------------------------------------------
#   Demo...
#-----------------------------------------------------------------------------------------


def one():
    time_grid = np.linspace(0, 250, 1700)
    a = 0.15
    hill_x1, hill_y1 = make_hill(a=a, time_grid=time_grid)
    plt.xlabel('Distance moved by x=log(infected population)')
    plt.ylabel('Altitude')
    plt.title('Epidemic Hill Climb')
    plt.plot(hill_x1, hill_y1)
    plt.legend(['a=' + str(round(a, 2)) for a in [a]])
    plt.show()

def two():
    time_grid = np.linspace(0, 250, 1700)
    aas = [0.0001, 0.1]
    hill_x1, hill_y1 = make_hill(a=aas[0], time_grid=time_grid)
    hill_x2, hill_y2 = make_hill(a=aas[1], time_grid=time_grid)

    plt.xlabel('Distance moved by x=log(infected population)')
    plt.ylabel('Altitude')
    plt.title('Epidemic Hill Climb')
    plt.plot(hill_x1, hill_y1, hill_x2, hill_y2)
    plt.legend(['a=' + str(round(a, 2)) for a in aas])
    plt.show()

if __name__=="__main__":
    one()

