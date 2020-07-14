from ddeint import ddeint
import numpy as np
from math import exp, ceil
import matplotlib.pyplot as plt


#----------------------------------------------------
#   Standalone compartmental model with delay DEs
#----------------------------------------------------


def novel_collision_probability(dt, a):
    return (1 - exp(-a * dt)) / (a * dt) if dt*a > 1e-4 else 1.0


def mean_attenuation(infection_func, t, g, a):
    """ Crudely estimate the mean attenuation

        Given a history of infections up to time t, this function tries to estimate the mean probability of the next collision being novel
        It is consistent with a physical model where particles make normal jumps from equi-spaced home locations on the plane.
        There are probably better ways to implement the system

    """
    if t*a<0.01:
        return 1.0
    else:
        t_high        =  t
        t_low         =  0
        num_interp_points = 5+int(ceil(t/2))
        ts             = np.linspace(t_low, t_high, num_interp_points)
        dt             = ts[1]-ts[0]
        its            = [infection_func(t_) for t_ in ts]
        net_new_its    = np.diff( [0]+its )
        new_its        = [ max(0,net_new + g*dt*existing) for net_new,existing in zip(net_new_its,its) ]   # Estimate of how many are new, taking into account those recovering

        scaling_factor = max( new_its + [1e-4] )
        scaled_new_its = [ ni/scaling_factor for ni in new_its ]

        survival       = [exp(-g * (t - t_)) for t_ in ts]  # Odds that they are still infected
        weights        = [ survive*it_+1e-4 for survive,it_ in zip(survival,scaled_new_its) ]  # Weighted
        sum_w          = sum(weights)
        normalized     = [ w/sum_w for w in weights ]
        assert abs(sum(normalized)-1)<1e-6, 'not normalized'
        att            = [w * novel_collision_probability(dt=t - t_, a=a) for w, t_ in zip(normalized, ts)]
        attenuation    = sum(att)
        return attenuation

def model(Y, t, a, b, g, dt ):
    """ SIR model with novelty attenuation """
    infection_func = lambda t: Y(t)[1]
    avg_attenuation = mean_attenuation(infection_func=infection_func,t=t,g=g,a=a)
    new_infections = Y(t)[0]*Y(t)[1]*(b*avg_attenuation)
    new_recoveries = Y(t)[1]*g
    attenuation_rate = (avg_attenuation-Y(t)[3])
    return [ -new_infections, new_infections-new_recoveries, new_recoveries, attenuation_rate ]


def values_before_zero(t):
    return [0.9999, 0.0001, 0.0, 1.0]

tt = np.linspace(0, 170, 500)

def moving_average(a, n=3) :
    ma = list()
    recent = list()
    for x in a:
        recent.append(x)
        if len(recent)>=n:
            recent.pop(0)
        ma.append(np.mean(recent))
    return ma


xs = [1,4,3,1,4,1,1,1,1]
ys = moving_average(xs,3)
len(ys)

def aplot(axs, a,logarithmic=False):
    import math
    b = 0.10+math.sqrt(0.02+math.pow(a,0.75))*0.135
    #b = 0.15
    g = 0.06
    dt = tt[1]-tt[0]
    derivatives = lambda Y,t : model(Y,t,a,b,g,dt)
    yy = ddeint(derivatives, values_before_zero, tt)
    infected    = yy.T[1]
    recovered   = yy.T[2]
    susceptible = yy.T[0]
    attenuation = yy.T[3]
    cases       = [ 1-s for s in susceptible ]

    eow1       = sum( t<7 for t in tt )
    eow2       = sum( t<14 for t in tt )
    eow1_cases = cases[eow1]
    eow2_cases = cases[eow2]
    total_cases = cases[-1]
    w1_growth  = (math.log(eow1_cases)-math.log(cases[0]))/7
    w2_growth  = (math.log(eow2_cases)-math.log(eow1_cases))/7

    peak_ndx   = np.argmax(infected)
    peak_susc  = susceptible[peak_ndx]
    peak_i     = infected[peak_ndx]
    Rn         = 1/peak_susc

    r  = 1-susceptible[-1]
    S0 = values_before_zero(0)[0]
    AR = 1-susceptible[-1]     # Attack rate
    Ri = - math.log((1-r)/S0)/(AR-(1-S0))  # https://bmcmedinformdecismak.biomedcentral.com/articles/10.1186/1472-6947-12-147
    analysis = {'a':a,'S0':S0,'R0':b/g,'AR':r,'Ri':Ri,'Rn':Rn,'w1_growth':w1_growth,'w2_growth':w2_growth,'tau':round(1/a,1),'peak_s':peak_susc,'peak_i':peak_i,'cases':total_cases}

    # Plot trajectory of infections and R numbers
    axs[0][0].plot(tt,100*infected)
    if logarithmic:
        axs[0][0].yscale('log')
    axs[0][0].figure
    axs[0][0].set_ylabel('Percentage infected')
    axs[0][0].set_title('R Values, Week 1,2 growth')
    axs[0][0].figure

    # Plot attenuation
    axs[0][1].axis([tt[0],tt[-1],0,1.01])
    axs[0][1].plot(tt, attenuation)
    axs[0][1].set_title('Attenuation')

    # Plot importance of attenuation versus herd effect
    axs[1][0].clear()
    axs[1][0].plot(tt, attenuation)
    axs[1][0].plot(tt, susceptible)
    axs[1][0].plot(tt, [ h/a for h,a in zip(susceptible,attenuation)])
    axs[1][0].plot(tt, [ h*a for h,a in zip(susceptible,attenuation)])
    axs[1][0].legend(['Local herd effect','Global herd effect','Relative importance of local','Combined effect'])
    axs[1][0].set_title('Herd Effects (a='+str(round(a,2))+')')
    axs[1][0].set_xlabel('Relative importance of local versus global herd effect')

    # Show acceleration
    axs[1][1].clear()
    dt = tt[1]-tt[0]
    position = [ math.log(i) for i in infected ]
    velocity = moving_average( np.gradient( position ), 10 )
    acceleration = moving_average( np.gradient( velocity ), 10 )

    dsus = np.gradient(susceptible)

    if a < 1e-5:
        force0 = [-b * ds * dt  for i, ds in zip(infected, dsus)]
    else:
        force0 = [-b * ds * dt * a for i, ds, a in zip(infected, dsus, attenuation)]

    if a<1e-5:
        force1 = [ b*b*i*s*dt*dt for i,s in zip(infected,susceptible) ]
    else:
        force1 = [ b*b*i*s*dt*dt*a*a for i,s,a in zip(infected,susceptible, attenuation) ]

    a_hill = hill(acceleration)

    if False:
        axs[1][1].plot(tt,[ -a for a in acceleration])
        axs[1][1].plot(tt,force0)
        #axs[1][1].plot(tt, force1)
        hill_scale  = max(np.abs(acceleration))/max(np.abs(a_hill))
        a_hill = [ hill_scale*h for h in a_hill ]
        axs[1][1].plot(tt,a_hill)
        axs[1][1].legend(['Acceleration','Force','Hill'])
        axs[1][1].set_xlabel('a='+str(round(a,2))+ ' tau='+str(round(1/a,1)))
        axs[1][1].set_title('Newton''s Law')

        axs[1][1].figure

    if True:
        # axs[1][1].plot(tt, force1)
        a_hill = hill(acceleration)
        axs[1][1].plot(tt, a_hill)
        axs[1][1].set_xlabel('a=' + str(round(a, 2)) + ' tau=' + str(round(1 / (0.000001+a), 1)))
        axs[1][1].set_title('Epidemic Hill (Stylized)')
        axs[1][1].figure


    return analysis


def hill(acceleration):
    y      = 0
    ys     = list()
    import math
    for a in acceleration:
        theta = math.asin(a)
        dy    = math.tan(theta)
        y     = y-dy
        ys.append(y)
    return ys





aas = np.linspace(10.0,10.0,1)

analysis = list()
legends = list()
fig, axs = plt.subplots(nrows=2,ncols=2)
for k,a in enumerate(aas):
    result = aplot(axs=axs,a=a)
    analysis.append( result )
    # Strings for labels
    R0s  = [ str(round(a['R0'],2)) for a in analysis ]
    Ris  = [ str(round(a['Ri'],2)) for a in analysis ]
    Rns  = [str(round(a['Rn'], 2)) for a in analysis]
    w1s  = [str(round(a['w1_growth'], 2)) for a in analysis]
    w2s  = [str(round(a['w2_growth'], 2)) for a in analysis]


    # Floats
    peak = [a['peak_i'] for a in analysis]
    cases = [a['cases'] for a in analysis]
    taus   = [a['tau'] for a in analysis]
    aas    = [a['a'] for a in analysis]

    # Set legends
    legend00 = ['R0='+R0+' Rn='+Rn+' Ri='+Ri +' w1='+w1 +' w2='+w2 for R0,Ri,Rn,w1,w2 in zip(R0s,Ris,Rns,w1s,w2s) ]
    axs[0][0].legend(legend00)
    legend01 = ['tau='+str(a['tau']) for a in analysis ]
    axs[0][1].legend(legend01)
    legend01 = ['tau=' + str(a['tau']) for a in analysis]
    axs[1][1].legend(legend01)

    # Plot error in peak infection estimate and total cases
    if k>0 and False:
        axs[1][1].clear()
        axs[1][1].plot( aas, [ cases[0]/c for c in cases], aas, [ peak[0]/p for p in peak]  )
        axs[1][1].legend(['Peak Infection','Total Cases'])
        axs[1][1].set_title('Predicted vs. Realized')
        axs[1][1].set_ylabel('Ratio to Realized')
        axs[1][1].set_xlabel('a')

    plt.show(block=False)
    plt.pause(0.2)


plt.show(block=True)



