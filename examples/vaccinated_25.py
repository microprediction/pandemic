from pandemic.example_parameters import TOY_TOWN
from pandemic.simulation import simulate
import matplotlib.pyplot as plt
import time

if __name__=="__main__":
    simulate(params=TOY_TOWN, plt=plt)
