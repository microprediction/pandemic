from pandemic.example_parameters import HOMESICK
from pandemic.conventions import DECEASED, POSITIVE, INFECTED, VULNERABLE
from pandemic.movement import evolve_positions, newly_exposed, times_of_day
from pandemic.plotting import plot_points
import matplotlib.pyplot as plt
import numpy as np
import math


# ------------------------------------------------------------------------------------
#   To illustrate the role of  kappa, W parameters and ergodic MS distance to home
# ------------------------------------------------------------------------------------


def circle(r,n=50):
    circle_x = [r*math.cos(theta) for theta in np.linspace(-math.pi, math.pi,num=n)]
    circle_y = [r*math.sin(theta) for theta in np.linspace(-math.pi, math.pi,num=n)]
    return circle_x, circle_y


def homesick(params):
    """ To illustrate the OU process  """

    num, num_initially_infected = int(params['geometry']['n']),int(params['geometry']['i'])
    num_times_of_day = int(params['motion']['t'])
    day_fraction = 1.0/num_times_of_day
    home = [(0,0) for _ in range(num) ]
    w    = params['motion']['w']
    k    = params['motion']['k']
    R    = w/math.sqrt(2*k)
    b    = params['geometry']['b']
    positions = [ (x/2*b,y/2*b) for x,y in [ tuple( np.random.multivariate_normal(mean=[0,0],cov=[[1,0],[0,1]]) ) for _ in range(num)] ]
    status    = [VULNERABLE]*num

    fig, axs = plt.subplots(nrows=1, ncols=2)
    population_variances = list()
    rolling_variances = list()
    for day in range(10):
        for step_no, time_of_day in enumerate(times_of_day(num_times_of_day)):
            stationary = [ s in [DECEASED, POSITIVE] for s in status ]
            positions  = evolve_positions(positions=positions, motion_params=params['motion'], attractors=home,
                                         day_fraction=day_fraction, stationary=stationary )

            axs[0].clear()
            plot_points(plt=axs[0], positions=positions, status=status, sizes=[64]*6)
            b = params['geometry']['b']
            axs[0].axis([-b, b, -b, b])
            axs[0].set_title('Day '+str(day))

            circle_x, circle_y = circle(r=R)
            axs[0].scatter(x=circle_x,y=circle_y,c='g',s=1)

            axs[0].figure

            population_variance = np.mean( [ x*x+y*y for x,y in positions ])
            population_variances.append(population_variance)

            num_lagged = 5+int(0.25*len(rolling_variances))
            rolling_mean_variance = np.mean( population_variances[-num_lagged:] )
            rolling_variances.append(rolling_mean_variance)

            axs[1].clear()
            axs[1].plot([ math.sqrt(v) for v in population_variances],'+')
            axs[1].plot([ math.sqrt(v) for v in rolling_variances] )
            axs[1].plot(list(range(len(rolling_variances))),[R]*len(rolling_variances),'--')
            axs[1].axis([0,len(rolling_variances),0.75*R,1.5*max(rolling_variances[-1],R)])
            axs[1].legend(['Current','Avg last ('+str(num_lagged)+')','Theoretical'],loc='upper left')
            axs[1].set_title('Root mean square distance')
            axs[1].figure


            plt.show(block=False)
            plt.pause(0.01)
            if step_no==1 and day==0:
                plt.pause(20)






if __name__=="__main__":
    homesick(params=HOMESICK)