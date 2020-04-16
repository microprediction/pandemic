from pandemic.example_parameters import INCEPTION
from pandemic.conventions import DECEASED, POSITIVE, INFECTED, VULNERABLE
from pandemic.movement import evolve_positions, newly_exposed, times_of_day
from pandemic.health import individual_progression, contact_progression
from pandemic.plotting import plot_points
import matplotlib.pyplot as plt
import numpy as np
import math
import random
from geohash import encode
from numpy.polynomial.polynomial import polyfit

# ------------------------------------------------------------------------------------
#   Standalone demonstration intended to illustrate the OU model within the OU model
# ------------------------------------------------------------------------------------


def circle(r,offset, n=50):
    circle_x = [r*math.cos(theta)+offset[0] for theta in np.linspace(-math.pi, math.pi,num=n)]
    circle_y = [r*math.sin(theta)+offset[1] for theta in np.linspace(-math.pi, math.pi,num=n)]
    return circle_x, circle_y

def sq_dist(pos1, pos2):
    return sum( [ (pos1[i]-pos2[i])*(pos1[i]-pos2[i]) for i in range(2) ] )

def intensity(params):
    """ To illustrate the OU process with commuting  """

    num, num_initially_infected = int(params['geometry']['n']), int(params['geometry']['i'])
    assert num % 2 ==0

    HOME_1  = (-1.5,1.5)
    HOME_2  = (-1.5,-1.5)
    HOME_3  = (1.5,1.5)
    HOME_4  = (1.5,-1.5)
    HOMES   = [ HOME_1, HOME_2, HOME_3, HOME_4 ]
    WORK    = (0,0)
    home    = [HOME_1]*int(num/4) + [HOME_2]*int(num/4) + [HOME_3]*int(num/4) + [HOME_4]*int(num/4)
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

    fig, axs = plt.subplots(nrows=2, ncols=2)


    population_variances = list()
    rolling_variances = list()
    collisions = list()
    rolling_mean_collisions = list()

    for day in range(50):
        for step_no, time_of_day in enumerate(times_of_day(num_times_of_day)):
            stationary = [ s in [DECEASED, POSITIVE] for s in status ]
            attractors = [ w for w in work ] if time_of_day<0.5 else [h for h in home]
            positions  = evolve_positions(positions=positions, motion_params=params['motion'], attractors=attractors,
                                          time_step=day_fraction, stationary=stationary)

            axs[0][0].clear()
            plot_points(plt=axs[0][0], positions=positions, status=status, sizes=[16]*6)
            b = params['geometry']['b']
            axs[0][0].axis([-b, b, -b, b])
            axs[0][0].axis([-b, b, -b, b])
            axs[0][0].set_title('Day '+str(day)+' '+str(time_of_day))

            for offsets in HOMES+[WORK]:
                circle_x, circle_y = circle(r=R,offset=offsets)
                axs[0][0].scatter(x=circle_x,y=circle_y,c='g',s=1)

            axs[0][0].figure

            # Collision count
            locations = [ encode(pos[0],pos[1],precision=6) for pos in positions ]
            num_collisions = num-len(set(locations))
            collisions.append(num_collisions)


            precision = 1.0/(params['motion']['w']**2)
            inv_sqs = [ np.mean([ 1./(0.00001+sq_dist(positions[j],pos)) for k,pos in enumerate(positions) if not j==k ]) for j in range(num) ]

            population_variances.append(np.mean(inv_sqs))

            num_lagged = 4*int(num_times_of_day/30)
            rolling_mean_variance = np.mean( population_variances[-num_lagged:] )
            rolling_mean_collisions.append( np.mean( collisions[-num_lagged:] ))
            rolling_variances.append(rolling_mean_variance)

            axs[0][1].clear()
            axs[0][1].plot([ math.sqrt(v) for v in population_variances],'x')
            axs[0][1].plot([ math.sqrt(v) for v in rolling_variances] )
            axs[0][1].plot(list(range(len(rolling_variances))),[R]*len(rolling_variances),'--')
            axs[0][1].legend(['Current time step','Avg last ('+str(num_lagged)+')'],loc='lower right')
            axs[0][1].set_title('Mean inverse squared distance)')
            axs[0][1].figure


            axs[1][1].plot(collisions,'+')
            axs[1][1].plot(rolling_mean_collisions,'--')
            axs[1][1].set_title('Collisions')
            axs[1][1].legend(['Current time step','Avg last ('+str(num_lagged)+')'],loc='upper left')
            axs[1][1].figure


            if day>0:
                rmc = rolling_mean_collisions[num_times_of_day:]
                pv  = population_variances[num_times_of_day:]
                axs[1][0].clear()
                axs[1][0].loglog(pv,rmc,'+')
                axs[1][0].set_xlabel('Mean inverse squared distance)')
                axs[1][0].set_ylabel('Mean collisions')
                b, m = polyfit(pv, rmc, 1)
                axs[1][0].plot(pv, [ b + m * pv_ for pv_ in pv], '-')
                axs[1][0].set_title('Slope is '+str(m))
                axs[1][0].figure

            if step_no % 2 == 0:
                plt.show(block=False)
                plt.pause(0.5)
                if step_no==1 and day==0:
                    plt.pause(5)






if __name__=="__main__":
    intensity(params=INCEPTION)