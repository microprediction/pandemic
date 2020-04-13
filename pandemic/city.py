
import random, math
import numpy as np

def sprawl( geometry_params, num ):
    """ Chinese restaurant inspired sprawl model """
    r = geometry_params['r']
    s = geometry_params['s']
    e = geometry_params['e']
    b = geometry_params['b']

    def bound(pos,b):
        return ( (pos[0]+b) % (2*b) - b , (pos[1]+b) % (2*b)  - b )

    def _neighbour(r, s, e, p, b ):
        """ Generate the next location, near to the position p
        :param r:   float          Typical distance to neighbour not including sprawl
        :param s:   float          Sprawl coef
        :param e:   float          Sprawl quadratic term
        :param p:   (float,float)  Neighbour
        :param b:   float          Bound
        :return: (float,float)
        """
        return bound( ( r*np.random.randn()+(1+s)*p[0]+e*p[0]*abs(p[0]) ,
                        r*np.random.randn()+(1+s)*p[1]+e*p[1]*abs(p[1])
               ),b=b)

    points = [ (0,0) ]
    for i in range(num-1):
        p = random.choice(points)
        points.append(_neighbour(r=r,s=s,e=e, p=p, b=b) )
    return points


def home_and_work_locations( geometry_params, num, centers=None ):

    def random_household_size(h):
        return 1 + np.random.binomial(n=6,p=(h-1)/8.0)

    if centers is None:
        b = geometry_params['b']
        centers = [ (b/2*np.random.rand(),b/2*np.random.rand()),(0,-b*np.random.rand())]

    # Sprawl work locations around centers
    work_sprawls = list()
    for center in centers:
        work_sprawls.append( [ (pos[0]+center[0], pos[1]+center[1]) for pos in sprawl( geometry_params=geometry_params, num=num) ] )
    work = [ random.choice(ws) for ws in zip( *work_sprawls ) ]

    # Sprawl homes away from centers also .. though further away
    geometry_params['r'] = 4 * geometry_params['r']
    home_sprawls = list()
    for center in centers:
        home_sprawls.append( [(pos[0] + center[0], pos[1] + center[1]) for pos in sprawl(geometry_params=geometry_params, num=num)])
    home_locations = [random.choice(hs) for hs in zip(*home_sprawls)]
    random.shuffle(home_locations)

    # Squeeze h people in each home.
    h = geometry_params['h']     # Avg number in household
    num_homes = int( math.ceil( num+500 / h ) )
    home = [ hl for hl in home_locations[:num_homes] for _ in range(random_household_size(h)) ][:num]

    # Some stay home
    c = geometry_params['c']
    work = [ w if np.random.rand()<c else h for w,h in zip(work,home) ]
    return home, work

if __name__=="__main__":
    import matplotlib.pyplot as plt
    for _ in range(20):
        plt.close()
        import time
        from pandemic.example_parameters import LARGE_TOWN
        from pandemic.plotting import plot_points
        city = sprawl(geometry_params=LARGE_TOWN['geometry'], num=50000)
        plot_points(plt, city, status=None)
        plt.axis([-20,20,-20,20])
        plt.show()
        plt.pause(0.001)
        time.sleep(1)
