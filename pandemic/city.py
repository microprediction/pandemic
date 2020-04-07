
import random
import numpy as np

def sprawl( geometry_params, num ):
    """ Chinese restaurant inspired sprawl model """
    r = geometry_params['r']
    s = geometry_params['s']
    e = geometry_params['e']

    def bound(pos):
        return ( (pos[0]+10) % 20 - 10 , (pos[1]+10) % 20  - 10 )

    def _neighbour(r, s, e, p):
        """
        :param r:   float          Typical distance to neighbour not including sprawl
        :param s:   float          Sprawl coef
        :param e:   float          Sprawl quadratic term
        :param p:   (float,float)  Neighbour
        :return: (float,float)
        """
        return bound( ( r*np.random.randn()+(1+s)*p[0]+e*p[0]*abs(p[0]) ,
                        r*np.random.randn()+(1+s)*p[1]+e*p[1]*abs(p[1])
               ))

    points = [ (0,0) ]
    for i in range(num-1):
        p = random.choice(points)
        points.append(_neighbour(r=r,s=s,e=e, p=p) )
    return points



def home_and_work_locations( geometry_params, num, centers=None ):

    if centers is None:
        centers = [ (1.1,7.5),(6,0),(0,7),(0,-5)]

    work_sprawls = list()
    for center in centers:
        work_sprawls.append( [ (pos[0]+center[0], pos[1]+center[1]) for pos in sprawl( geometry_params=geometry_params, num=num) ] )
    work = [ random.choice(ws) for ws in zip( *work_sprawls ) ]

    geometry_params['r'] = 4 * geometry_params['r']
    home_sprawls = list()
    for center in centers:
        home_sprawls.append( [(pos[0] + center[0], pos[1] + center[1]) for pos in sprawl(geometry_params=geometry_params, num=num)])
    home = [random.choice(hs) for hs in zip(*home_sprawls)]

    work = [ random.choice([w,h]) for w,h in zip(work,home) ]   # Half stay home
    return home, work

if __name__=="__main__":
    import matplotlib.pyplot as plt
    from pandemic.conventions import EXAMPLE_PARAMETERS
    from pandemic.plotting import plot_points
    city = sprawl(geometry_params=EXAMPLE_PARAMETERS['geometry'], num=500)
    plot_points(plt, city, status=None)
    plt.show()