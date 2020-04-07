from collections import OrderedDict

EXAMPLE_PARAMETERS = {
                       'geometry':{'n':20000,'i':50,'r':0.04,'d':5,'s':0.25,'e':0.05,'p':6},
                       'motion':{'t':24,'k':3.0,'w':1.0,'c':0.5},
                       'health':{'vi':1.0,'is':0.2,'ip':0.5/14,'sp':1.0,'ir':0.995/14,'id':0.005/14,'sr':0.98/14,'sd':0.02/14,'pd':0.02/14,'pr':0.96/14}
                      }

STATE_DESCRIPTIONS     = OrderedDict( {'v':'vulnerable','i':'infected','s':'symptomatic','p':'positive','r':'recovered','d':'dead'} )
STATE_COLORS           = ['y','c', 'b', 'm', 'r', 'k']
GEOMETRY_DESCRIPTIONS  = OrderedDict({'n':'Population count','i':'Number initially infected','r': 'Sprawl distance', 'd': 'Distance from work to home','s':'Sprawl linear coefficient','e':'Sprawl quadratic term'} )
MOTION_DESCRIPTIONS    = OrderedDict({'T':'Number of time steps in a day','k':'fractional distance moved towards attractor per day (kappa)','w':'standard deviation per day (brownian motion term)'} )
HEALTH_DESCRIPTIONS   = OrderedDict({ 'vi':'Infection probability if exposed',
                                      'is':'Symptom rate if infected',
                                      'ip':'Randomized testing rate multiplied by probability of being positive if infected but asymptomatic',
                                      'sp':'Symptomatic testing rate multiplied by probability of being positive if symptomatic',
                                      'ir':'Asymptomatic recovery rate',
                                      'sr':'Symptomatic recovery rate',
                                      'sd':'Symptomatic death rate',
                                      'id':'Asymptomatic death rate',
                                      'pd':'Positive death rate',
                                      'pr':'Positive recovery rate'})  # All rates are per day.
STATES    = list(STATE_DESCRIPTIONS.keys())
GEOMETRY  = list(GEOMETRY_DESCRIPTIONS.keys())
MOTION    = list(MOTION_DESCRIPTIONS.keys())
HEALTH    = list(HEALTH_DESCRIPTIONS.keys())
VULNERABLE, INFECTED, SYMPTOMATIC, POSITIVE, RECOVERED, DEAD = 0, 1, 2, 3, 4, 5
HOME, WORK = 0, 1

NUM_STATES, NUM_GEOMETRY, NUM_MOTION, NUM_HEALTH  = len(STATE_DESCRIPTIONS), len(GEOMETRY_DESCRIPTIONS), len(MOTION), len(HEALTH)



