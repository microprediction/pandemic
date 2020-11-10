from pandemic.example_parameters import CIR, SPHERE_1, SPHERE_2, SPHERE_3, DISK, TOWN
import matplotlib.pyplot as plt
import numpy as np
import math
import random, copy
from pandemic.simulation import simulate
from pandemic.surrogate import status_counts
from pandemic.plotting import plot_points
from pandemic.conventions import INFECTED, POSITIVE, RECOVERED, VULNERABLE

# ----------------------------------------------------------------------
#    Attenuation and unique collisions
# ----------------------------------------------------------------------

def equal_spaced_homes(b,num):
    num1 = int(math.sqrt(num))
    return [ (x,y) for x in np.linspace(-b,b,num1) for y in np.linspace(-b,b,num1) ]

class Plane():

    def __init__(self, params,plt, axs, legend, color):
        self.params = params
        self.metric_history = list()
        self.time_history = list()
        self.collision_history = list()
        self.collision_daily_history = list()
        self.plt = plt
        self.axs  = axs
        self.legend = legend
        self.color = color
        w = params['motion']['w']
        k = params['motion']['k']
        self.w = 6*w
        self.R = w / math.sqrt(2 * k)
        self.home = equal_spaced_homes(b=params['geometry']['b'], num=params['geometry']['n'])
        self.params['geometry']['n'] = len(self.home)
        from copy import deepcopy
        self.work = [ (0,0) for h in self.home ]
        self.params['geometry']['c']= 1.0
        self.initial_positions = deepcopy(self.home)
        self.num_joes = 30 # Number of people like Joe and Mary to track uniques
        self.friends = [ set() for _ in range(self.num_joes) ]
        self.collision_history =  list()
        self.unique_collions_history =  list()
        self.attenuation_history = list()
        self.herd_history = list()

    def callback(self, day, day_fraction, status, positions, home, work, plt, **ignore_other_kwargs):
        """ This gets called after each computation cycle (see pandemic/simulation.py) """
        from pandemic.metrics import collision_count
        # Unique collisions with Joe
        from geohash import encode

        approx_precision = self.params['geometry']['p'] - 2

        for joe in range(self.num_joes):
            joes_hash = encode( positions[joe][0],positions[joe][1], precision = approx_precision )
            rough_positions = [ ( encode(pos[0], pos[1], precision=self.params['geometry']['p']-2),j) for j,pos in enumerate(positions) ]
            joes_collisions = [ j for (h,j) in rough_positions if h==joes_hash and not j==joe ]
            joes_new_collisions = [j for j in joes_collisions if not j in self.friends[joe] ]
            self.friends[joe].update( joes_new_collisions )
            self.collision_history.append(len(joes_collisions))
            self.unique_collions_history.append(len(joes_new_collisions))
        num_rolling = 48
        if len(self.collision_history)>num_rolling*self.num_joes:
            rolling_collisions = sum(self.collision_history[-num_rolling*self.num_joes:])
            rolling_unique_collisions = sum(self.unique_collions_history[-num_rolling*self.num_joes:])
            if day_fraction==0:
                self.attenuation_history.append((0.1 + rolling_unique_collisions) / (0.1 + rolling_collisions))
                self.herd_history.append(sum([s in [VULNERABLE] for s in status]) / len(status))

        if day_fraction==0:
            # Daily collision TS
            self.collision_daily_history.append(sum(self.collision_history[-self.params['motion']['t']:]))


            # Standard plot of infections
            metrics = status_counts(status=status)
            self.metric_history.append(metrics)
            self.time_history.append(day + day_fraction)
            self.axs[0][0].clear
            plot_points(plt=self.axs[0][0],positions=positions,status=status,title='Ornstein-Uhlenbeck')
            self.axs[0][0].figure

            if day > 1:
                # Collisions curve
                self.axs[1][0].plot(self.attenuation_history,marker='*')
                self.axs[1][0].plot(self.herd_history, marker='o')
                self.axs[1][0].set_title('Novelty versus Herd effect')


                self.axs[1][0].set_xlabel('Days since ' + str(self.params['geometry']['i']) + ' cases.')
                self.axs[1][0].set_ylabel('Attenuation')
            # Growth curve
            infect = [m[1] for m in self.metric_history]
            self.axs[0][1].plot(self.time_history, infect,color=self.color)
            #self.axs[0][1].set_yscale('log')
            self.axs[0][1].set_title('Infected')
            self.axs[0][1].figure

            if day>1:
                # Collisions curve
                self.axs[1][1].plot(self.collision_daily_history, color=self.color, marker='*')
                self.axs[1][1].set_title('Daily collisions')
                self.axs[1][1].set_xlabel('Days since '+str(self.params['geometry']['i'])+' cases.')

            self.plt.show(block=False)
            figManager = plt.get_current_fig_manager()
            figManager.full_screen_toggle()
            self.plt.pause(2)


    def run(self):
        """ To illustrate the OU process  """
        self.axs[0][0].clear()
        simulate(params=self.params,plt=plt,callback=self.callback,home=self.home,work=self.work, positions=self.initial_positions, stopping_t=150)


def growth_comparisons(after_day=9,b=3):
    ns = list(np.linspace(0.85,1.15,7*20))
    growth = list()
    growth_abscissa = list()
    log_collisions  = list()
    fig, axs = plt.subplots(nrows=2,ncols=2)
    colors = ['blue','green','red','cyan','magenta','yellow','black']*20
    for i, n in enumerate(ns):
        params = copy.deepcopy(TOWN)
        params['geometry']['b'] = b
        params['geometry']['n'] = 1450

        dsk = Plane(params=params, plt=plt, axs=axs, legend=[str(n_) for n_ in ns[:i]], color=colors[i])
        dsk.run()

        metrics = dsk.metric_history[:after_day][-1]
        infections_after = metrics[1]
        growth.append(infections_after)
        growth_abscissa.append(math.log(n))
        axs[0][2].clear()
        log_growth = [ math.log(math.log(g)) for g in growth]

        clsn = dsk.collision_daily_history[:after_day][-1]
        log_collisions.append(math.log(0.1+clsn))
        axs[1][2].plot(growth_abscissa, log_collisions, '*')
        axs[1][2].figure

        if i>=1:
            # Log Log infections against Log population
            poly_1 = np.poly1d(np.polyfit(growth_abscissa, log_growth, 1))
            best_fit_1 = poly_1(growth_abscissa)
            axs[0][2].plot(growth_abscissa, log_growth, '*')
            axs[0][2].plot(growth_abscissa,best_fit_1,'-')
            axs[0][2].set_title('Coefficients '+str(poly_1.coef))
            axs[0][2].set_xlabel('Log( Population )')
            axs[0][2].set_ylabel('Log( Log(infections) ) after '+str(after_day)+' days')

            # Log collisions against Log population
            if True:
                poly_2 = np.poly1d(np.polyfit(growth_abscissa, log_collisions, 1))
                best_fit_2 = poly_2(growth_abscissa)
                axs[1][2].clear()
                axs[1][2].plot(growth_abscissa, log_collisions,'*')
                axs[1][2].plot(growth_abscissa, best_fit_2, '-')
                axs[1][2].set_title('Coefficients ' + str(poly_2.coef))
                axs[1][2].set_xlabel('Log( Population )')
                axs[1][2].set_ylabel('Log( Collisions ) after ' + str(after_day) + ' days')
            
        plt.show(block=False)
        plt.pause(0.1)



if __name__=="__main__":
    growth_comparisons()


