from pandemic.example_parameters import CIR, SPHERE_1, SPHERE_2, SPHERE_3, DISK
import matplotlib.pyplot as plt
import numpy as np
import math
import random, copy
from pandemic.simulation import simulate
from pandemic.surrogate import status_counts
from pandemic.plotting import plot_points


# ----------------------------------------------------------------------
#    Study of a disk population and effect of density on growth rates
# ----------------------------------------------------------------------


def circle(r, n=50):
    circle_x = [r * math.cos(theta) for theta in np.linspace(-math.pi, math.pi, num=n)]
    circle_y = [r * math.sin(theta) for theta in np.linspace(-math.pi, math.pi, num=n)]
    return circle_x, circle_y


def initialization(params):
    num = params['geometry']['n']
    home = [(0, 0) for _ in range(num)]
    work = [(0, 0) for _ in range(num)]
    w = params['motion']['w']
    k = params['motion']['k']
    R = w / math.sqrt(2 * k)
    R = 100 * params['geometry']['r']

    home = [(x / 2 * R, y / 2 * R) for x, y in
            [tuple(np.random.multivariate_normal(mean=[0, 0], cov=[[1, 0], [0, 1]])) for _ in range(num)]]

    return home, work


class Disk():

    def __init__(self, params, plt, axs, legend, color):
        self.params = params
        self.metric_history = list()
        self.time_history = list()
        self.collision_history = list()
        self.collision_daily_history = list()
        self.plt = plt
        self.axs = axs
        self.legend = legend
        self.color = color
        w = params['motion']['w']
        k = params['motion']['k']
        self.w = w
        self.R = w / math.sqrt(2 * k)

    def callback(self, day, day_fraction, status, positions, home, work, plt, **ignore_other_kwargs):
        """ This gets called after each computation cycle (see pandemic/simulation.py) """
        from pandemic.metrics import collision_count
        cc = collision_count(positions=positions, status=status, precision=self.params['geometry']['p'])
        self.collision_history.append(cc)
        if day_fraction == 0:
            # Daily collision TS
            self.collision_daily_history.append(sum(self.collision_history[-self.params['motion']['t']:]))

            # Standard plot of infections
            metrics = status_counts(status=status)
            self.metric_history.append(metrics)
            self.time_history.append(day + day_fraction)
            self.axs[0][0].clear
            plot_points(plt=self.axs[0][0], positions=positions, status=status, title='Ornstein-Uhlenbeck')
            self.axs[0][0].figure

            # Standard plot of vulnerable only
            metrics = status_counts(status=status)
            vulnerable_positions = [pos for pos, s in zip(positions, status) if s == 0]
            vulnerable_status = [s for s in status if s == 0]

            # Counts plot
            self.metric_history.append(metrics)
            self.time_history.append(day + day_fraction)
            self.axs[1][0].clear()
            plot_points(plt=self.axs[1][0], positions=vulnerable_positions, status=vulnerable_status,
                        title='Vulnerable')
            self.axs[1][0].figure

            # Growth curve
            infect = [m[1] for m in self.metric_history]
            self.axs[0][1].plot(self.time_history, infect, color=self.color)
            # self.axs[0][1].set_yscale('log')
            self.axs[0][1].set_title('Infected')
            self.axs[0][1].figure

            if day > 1:
                # Collisions curve
                self.axs[1][1].plot(self.collision_daily_history, color=self.color)
                self.axs[1][1].set_title('Collisions per day')
                self.axs[1][1].set_xlabel('Days since ' + str(self.params['geometry']['i']) + ' cases.')

            self.plt.show(block=False)
            self.plt.pause(0.1)

    def run(self):
        """ To illustrate the OU process  """
        self.axs[0][0].clear()
        home, work = initialization(self.params)
        simulate(params=self.params, plt=plt, callback=self.callback, home=home, work=work, stopping_t=50)


def growth_comparisons(after_day=9):
    ns = list(np.linspace(0.85, 1.15, 7 * 20))
    growth = list()
    growth_abscissa = list()
    log_collisions = list()
    fig, axs = plt.subplots(nrows=2, ncols=3)
    colors = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black'] * 20
    for i, n in enumerate(ns):
        params = copy.deepcopy(DISK)
        params['geometry']['n'] = int(4000 * n)
        dsk = Disk(params=params, plt=plt, axs=axs, legend=[str(n_) for n_ in ns[:i]], color=colors[i])
        dsk.run()

        metrics = dsk.metric_history[:after_day][-1]
        infections_after = metrics[1]
        growth.append(infections_after)
        growth_abscissa.append(math.log(n))
        axs[0][2].clear()
        log_growth = [math.log(math.log(g)) for g in growth]

        clsn = dsk.collision_daily_history[:after_day][-1]
        log_collisions.append(math.log(clsn))
        axs[1][2].plot(growth_abscissa, log_collisions, '*')
        axs[1][2].figure

        if i >= 1:
            # Log Log infections against Log population
            poly_1 = np.poly1d(np.polyfit(growth_abscissa, log_growth, 1))
            best_fit_1 = poly_1(growth_abscissa)
            axs[0][2].plot(growth_abscissa, log_growth, '*')
            axs[0][2].plot(growth_abscissa, best_fit_1, '-')
            axs[0][2].set_title('Coefficients ' + str(poly_1.coef))
            axs[0][2].set_xlabel('Log( Population )')
            axs[0][2].set_ylabel('Log( Log(infections) ) after ' + str(after_day) + ' days')

            # Log collisions against Log population
            if True:
                poly_2 = np.poly1d(np.polyfit(growth_abscissa, log_collisions, 1))
                best_fit_2 = poly_2(growth_abscissa)
                axs[1][2].clear()
                axs[1][2].plot(growth_abscissa, log_collisions, '*')
                axs[1][2].plot(growth_abscissa, best_fit_2, '-')
                axs[1][2].set_title('Coefficients ' + str(poly_2.coef))
                axs[1][2].set_xlabel('Log( Population )')
                axs[1][2].set_ylabel('Log( Collisions ) after ' + str(after_day) + ' days')

        plt.show(block=False)
        plt.pause(0.1)


if __name__ == "__main__":
    growth_comparisons()
