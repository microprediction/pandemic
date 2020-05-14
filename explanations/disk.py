from pandemic.example_parameters import CIR, SPHERE_1, SPHERE_2, SPHERE_3
from pandemic.conventions import DECEASED, POSITIVE, INFECTED, VULNERABLE
from pandemic.movement import evolve_positions, newly_exposed, times_of_day
from pandemic.conventions import STATE_DESCRIPTIONS
from pandemic.plotting import plot_points
import matplotlib.pyplot as plt
import numpy as np
import math
import random
from pprint import pprint
from pandemic.simulation import simulate
from pandemic.surrogate import status_counts

# -------------------------------------------
#    On the CIR model and how it relates
# -------------------------------------------

def circle(r,n=50):
    circle_x = [r*math.cos(theta) for theta in np.linspace(-math.pi, math.pi,num=n)]
    circle_y = [r*math.sin(theta) for theta in np.linspace(-math.pi, math.pi,num=n)]
    return circle_x, circle_y

def initialization(params):
    num = params['geometry']['n']
    home = [(0, 0) for _ in range(num)]
    work = [(0, 0) for _ in range(num)]
    w = params['motion']['w']
    k = params['motion']['k']
    R = w / math.sqrt(2 * k)
    positions = [(x / 2 * R, y / 2 * R) for x, y in
                 [tuple(np.random.multivariate_normal(mean=[0, 0], cov=[[1, 0], [0, 1]])) for _ in range(num)]]
    return home, work, positions

class Ergodic():

    def __init__(self, params,plt):
        self.params = params
        self.metric_history = list()
        self.time_history = list()
        self.plt = plt
        w = params['motion']['w']
        k = params['motion']['k']
        self.R = w / math.sqrt(2 * k)
        if plt is not None:
            self.fig, self.axs = plt.subplots(nrows=2, ncols=2)

    def plot_metrics(self, plt, logarithmic, differences=False):
        metrics = list(zip(*self.metric_history))[1:]
        if len(metrics[0]) > 3:
            for m in metrics[1:-2]:
                if differences:
                    plt.plot(self.time_history[1:], list(np.diff(m)))
                    plt.set_ylabel('Daily change')
                else:
                    plt.plot(self.time_history, m)
                    plt.set_ylabel('Cumulative')
            if logarithmic:
                plt.set_yscale('log')
            labels = list(STATE_DESCRIPTIONS.values())[1:-2]
            if differences:
                labels = ['net newly ' + lb for lb in labels]
            plt.legend(labels)
            plt.set_xlabel('Days since first ' + str(self.params['geometry']['i']) + ' infections.')

    def plot(self, plt, positions, status):

        # Population plot
        self.axs[0][0].clear()
        plot_points(plt=self.axs[0][0], positions=positions, status=status)
        circle_x, circle_y = circle(r=self.R)
        self.axs[0][0].scatter(x=circle_x, y=circle_y, c='g', s=1)
        self.axs[0][0].figure

        # Metrics plots, regular and logarithmic
        for k in range(2):
            self.axs[1][k].clear()
            self.plot_metrics(plt=self.axs[1][k], logarithmic=k)
            self.axs[1][k].figure

        # Rates of change
        self.axs[0][1].clear()
        self.plot_metrics(plt=self.axs[0][1], logarithmic=False, differences=True)
        self.axs[0][1].figure

        plt.show(block=False)
        plt.pause(0.1)

    def callback(self, day, day_fraction, status, positions, home, work, plt, **ignore_other_kwargs):
        """ This gets called after each computation cycle (see pandemic/simulation.py) """
        if day_fraction==0:
            metrics = status_counts(status=status)
            self.metric_history.append(metrics)
            self.time_history.append(day + day_fraction)
            if self.plt is not None:
                self.plot(plt=plt, positions=positions, status=status)
            pprint({"day": str(day + day_fraction), "metrics":metrics})
            print(' ', flush=True)
        if False:
            positions = random.shuffle(positions)
        if day==0:
            import time
            time.sleep(10)

    def run(self):
        """ To illustrate the OU process  """
        home, work, positions = initialization(self.params)
        simulate(params=self.params,plt=plt,callback=self.callback,home=home,work=work,positions=positions)




if __name__=="__main__":
    params = SPHERE_3
    erg = Ergodic(params=SPHERE_3,plt=plt)
    erg.run()

