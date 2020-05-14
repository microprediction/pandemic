import copy
# Examples of system parameters. See /conventions.py for meaning
from pandemic.conventions import DESCRIPTIONS


STANDARD_HEALTH_PARAMS = {'vi':1.0,'is':0.1,'ip':0.025,'sp':0.2,'ir':0.995/14,'id':0.005/14,'sr':0.97/14,'sd':0.03/14,'pd':0.02/14,'pr':0.96/14}

SMALL_CITY = {
           'geometry':{'n':800000,'i':500,'r':0.005,'b':15,'h':2.5,'c':0.5,'s':0.25,'e':0.0005,'p':8},
           'motion':{'t':24,'k':3.0,'w':0.01},
           'health':copy.deepcopy(STANDARD_HEALTH_PARAMS)
}

CITY = copy.deepcopy(SMALL_CITY)

LARGE_TOWN = {
           'geometry':{'n':40000,'i':50,'r':0.04,'b':25,'h':2.5,'c':0.5,'s':0.25,'e':0.05,'p':6},
           'motion':{'t':24,'k':3.0,'w':1.0},
           'health':copy.deepcopy(STANDARD_HEALTH_PARAMS)
}

TOWN = copy.deepcopy( LARGE_TOWN )

CIR = {
           'geometry':{'n':40000,'i':50,'r':0.04,'b':25,'h':2.5,'c':0.5,'s':0.25,'e':0.05,'p':6},
           'motion':{'t':24,'k':3.0,'w':1.0},
           'health':copy.deepcopy(STANDARD_HEALTH_PARAMS)
}
CIR['health']['vi']=0.1

# Without mixing
SPHERE_1 = copy.deepcopy(CIR)
SPHERE_1['motion']['k']  = 0.00325 * SPHERE_1['motion']['k']
SPHERE_1['health']['vi'] = 0.25    * SPHERE_1['health']['vi']  # Infection probability upon collision

# Close to R=1 for mixing but grows ever so slowly
SPHERE_2 = copy.deepcopy(CIR)
SPHERE_2['motion']['k']  = 0.00325 * SPHERE_2['motion']['k']
SPHERE_2['health']['vi'] = 0.75*SPHERE_2['health']['vi']  # Infection probability upon collision

# Mixing
SPHERE_3 = copy.deepcopy(CIR)
SPHERE_3['motion']['w']  = 0.70 * SPHERE_3['motion']['w']
SPHERE_3['motion']['k']  = 0.00325 * SPHERE_3['motion']['k']
SPHERE_3['health']['vi'] = 1.0*SPHERE_3['health']['vi']  # Infection probability upon collision


SPHERE_3 = copy.deepcopy(CIR)
SPHERE_3['motion']['w']  = 0.25*0.70 * SPHERE_3['motion']['w']
SPHERE_3['geometry']['n'] = 5000
SPHERE_3['motion']['k']  = 0.00325 * SPHERE_3['motion']['k']
SPHERE_3['health']['vi'] = 1.0*SPHERE_3['health']['vi']  # Infection probability upon collision

# Density study
DISK = {
           'geometry':{'n':4500,'i':50,'r':0.05,'b':25,'h':2.5,'c':0.5,'s':0.25,'e':0.05,'p':6},
           'motion':{'t':24,'k':3.0,'w':0.3},
           'health':copy.deepcopy(STANDARD_HEALTH_PARAMS)
}
DISK['health']['vi']=0.5

# Examples to help illustrate the model

TOY_TOWN = {
           'geometry':{'n':50,'i':5,'r':3.0,'b':20,'h':2.5,'c':0.5,'s':0.25,'e':0.05,'p':4},
           'motion':{'t':240,'k':3.0,'w':3.0},
           'health':{'vi':1.0,'is':0.1,'ip':0.025,'sp':0.2,'ir':0.995/14,'id':0.005/14,'sr':0.97/14,'sd':0.03/14,'pd':0.02/14,'pr':0.96/14}
}



HOMESICK = {
           'geometry':{'n':50,'i':5,'r':1.0,'b':1,'h':2.5,'c':0.5,'s':0.25,'e':0.05,'p':4},
           'motion':{'t':240,'k':3.0,'w':1.0},
           'health':{'vi':1.0,'is':0.1,'ip':0.025,'sp':0.2,'ir':0.995/14,'id':0.005/14,'sr':0.97/14,'sd':0.03/14,'pd':0.02/14,'pr':0.96/14}
}

WORKSICK = {
           'geometry':{'n':50,'i':5,'r':1.0,'b':3,'h':2.5,'c':0.5,'s':0.25,'e':0.05,'p':4},
           'motion':{'t':100,'k':10.0,'w':3.0},
           'health':{'vi':1.0,'is':0.1,'ip':0.025,'sp':0.2,'ir':0.995/14,'id':0.005/14,'sr':0.97/14,'sd':0.03/14,'pd':0.02/14,'pr':0.96/14}
}

INCEPTION = {
           'geometry':{'n':1000,'i':5,'r':1.0,'b':3,'h':2.5,'c':0.5,'s':0.25,'e':0.05,'p':6},
           'motion':{'t':100,'k':6.0,'w':2},
           'health':{'vi':1.0,'is':0.1,'ip':0.025,'sp':0.2,'ir':0.995/14,'id':0.005/14,'sr':0.97/14,'sd':0.03/14,'pd':0.02/14,'pr':0.96/14}
}




BASELINES = {'large_town':LARGE_TOWN,
             'town':TOWN,
             'city':CITY,
             'small_city':SMALL_CITY,
             'toy_town':TOY_TOWN}

def modifier( category, param, factor, baseline):
    # Returns modified town params and description of how it was modified
    params = copy.deepcopy(BASELINES[baseline])
    cat_params = params[category]
    cat_params[param] = cat_params[param]*factor
    params[category] = cat_params
    description = (DESCRIPTIONS[category][param] + ' multiplied by ' + str(factor))
    return params, description