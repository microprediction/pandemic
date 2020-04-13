from pandemic.example_parameters import SMALL_CITY
from pandemic.simulation import simulate
import matplotlib.pyplot as plt

if __name__=="__main__":
    simulate(params=SMALL_CITY, plt=plt)
