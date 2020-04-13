from pandemic.example_parameters import LARGE_TOWN
from pandemic.simulation import simulate
import matplotlib.pyplot as plt

def large_town(with_plot=True):
    simulate(params=LARGE_TOWN, plt=plt if with_plot else None)

def small_town(with_plot=True):
    params = LARGE_TOWN
    params['geometry']['n']= int( params['geometry']['n'] / 2 )
    simulate(params=params, plt=plt if with_plot else None)

def town_that_tests_symptomatic_more(with_plot=True):
    params = LARGE_TOWN
    params['health']['sp']= 3*params['health']['sp']
    simulate(params=params, plt=plt if with_plot else None)

def town_that_tests_randomly(with_plot=True):
    params = LARGE_TOWN
    params['health']['sp']= 3*params['health']['sp']
    params['health']['ip'] =6*params['health']['ip']
    simulate(params=params, plt=plt if with_plot else None)

def town_with_close_neighbours(with_plot=True):
    params = LARGE_TOWN
    params['geometry']['r']= 0.5*params['geometry']['r']   # Sprawl distance
    simulate(params=params, plt=plt if with_plot else None)


if __name__=="__main__":
    large_town()
