import matplotlib.pyplot as plt
import numpy as np

#---------------------------------------------------------
#   Illustrates harmonic mean ratio for contagiousness
#---------------------------------------------------------

def tent(b):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    roof_plot(ax=ax,b=b)
    plt.show()

def roof_plot(ax,b):
    r = np.linspace(0, b, 50)
    p = np.linspace(0, 2 * np.pi, 50)
    R, P = np.meshgrid(r, p)
    Z = 1-R
    X, Y = R * np.cos(P), R * np.sin(P)
    ax.plot_surface(X, Y, Z)
    ax.set_zlim(0,1)
    ax.figure




if __name__=="__main__":
    tent(b=0.6)