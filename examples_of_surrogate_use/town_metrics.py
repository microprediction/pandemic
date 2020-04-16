from pandemic.surrogate import Surrogate
import matplotlib.pyplot as plt

# Example of retrieving time series of metrics stored at www.swarmprediction.com

PARAMS = {'geometry': {'b': 25,
              'c': 0.39819124674450257,
              'e': 0.05,
              'h': 2.5,
              'i': 50,
              'n': 40000,
              'p': 6,
              'r': 0.04,
              's': 0.25},
 'health': {'id': 0.00035714285714285714,
            'ip': 0.025,
            'ir': 0.07107142857142858,
            'is': 0.1,
            'pd': 0.0014285714285714286,
            'pr': 0.06857142857142857,
            'sd': 0.002142857142857143,
            'sp': 0.1001594618899572,
            'sr': 0.06928571428571428,
            'vi': 1.0},
 'motion': {'k': 3.0, 't': 24, 'w': 0.916013618644953}}


if __name__=="__main__":
    s = Surrogate(params=PARAMS)
    s.plot_metrics(plt=plt)