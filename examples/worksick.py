from pandemic.example_parameters import WORKSICK
from pandemic.conventions import DECEASED, POSITIVE, INFECTED, VULNERABLE
from pandemic.movement import evolve_positions, newly_exposed, times_of_day
from pandemic.health import individual_progression, contact_progression
from pandemic.plotting import plot_points
import matplotlib.pyplot as plt
import numpy as np
import math
import random

# ------------------------------------------------------------------------------------
#   Standalone demonstration intended to illustrate the role of  kappa, W parameters
# ------------------------------------------------------------------------------------


def circle(r,offset, n=50):
    circle_x = [r*math.cos(theta)+offset[0] for theta in np.linspace(-math.pi, math.pi,num=n)]
    circle_y = [r*math.sin(theta)+offset[1] for theta in np.linspace(-math.pi, math.pi,num=n)]
    return circle_x, circle_y

def sq_dist(pos1, pos2):
    return sum( [ (pos1[i]-pos2[i])*(pos1[i]-pos2[i]) for i in range(2) ] )

def commute(params):
    """ To illustrate the OU process with commuting  """

    num, num_initially_infected = int(params['geometry']['n']), int(params['geometry']['i'])
    assert num % 2 ==0

    HOME_1  = (-1.5,1.5)
    HOME_2  = (-1.5,-1.5)
    WORK    = (1.5,0)
    home    = [HOME_1]*int(num/2) + [HOME_2]*int(num/2)
    work    = [WORK]*num

    def is_working(time_of_day):
        return time_of_day>0.4 and time_of_day<0.6

    def is_home(time_of_day):
        return time_of_day<0.0 or time_of_day>0.75

    num, num_initially_infected = int(params['geometry']['n']),int(params['geometry']['i'])
    num_times_of_day = int(params['motion']['t'])
    day_fraction = 1.0/num_times_of_day
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
            attractors = [ w for w in work ] if time_of_day<0.5 else [h for h in home]
            positions  = evolve_positions(positions=positions, motion_params=params['motion'], attractors=attractors,
                                         day_fraction=day_fraction, stationary=stationary )

            axs[0].clear()
            plot_points(plt=axs[0], positions=positions, status=status, sizes=[64]*6)
            b = params['geometry']['b']
            axs[0].axis([-b, b, -b, b])
            axs[0].set_title('Day '+str(day)+' '+str(time_of_day))

            for offsets in [HOME_1,HOME_2,WORK]:
                circle_x, circle_y = circle(r=R,offset=offsets)
                axs[0].scatter(x=circle_x,y=circle_y,c='g',s=1)

            axs[0].figure

            if is_home(time_of_day):
                population_variance = np.mean( [ sq_dist(pos, hm) for pos,hm in zip(positions,home) ] )

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
                axs[1].set_title('RMS Distance to home after 6pm')
                axs[1].figure


            plt.show(block=False)
            plt.pause(0.01)
            if step_no==1 and day==0:
                plt.pause(20)






if __name__=="__main__":
    commute(params=WORKSICK)