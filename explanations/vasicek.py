
import matplotlib.pyplot as plt
from math import exp
import numpy as np

def tau(t,kappa):
    if kappa>0:
        return (1-exp(-kappa*t))/kappa
    else:
        return t

def tautont(t,kappa):
    if t>0:
        return tau(t,kappa)/t
    else:
        return 1.0

def demo():
    ts = np.linspace(0,30,10)
    flat = [ 1 for t in ts ]
    fade = [ tautont(t,0.02) for t in ts ]
    curv = [ -0.005*0.5*tautont(t,0.02)*tau(t,0.02)/(0.02) for t in ts ]
    plt.plot(ts,flat, ts,fade, ts,curv)
    plt.legend(['Flat','Attenuation','Variation'])
    plt.title('Basis for Early Stage Growth')
    plt.xlabel('Days')
    plt.show()


if __name__=="__main__":
    demo()