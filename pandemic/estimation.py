from pandemic.conventions import GEOMETRY, NUM_GEOMETRY, HEALTH, MOTION, NUM_MOTION, NUM_STATES

# Work in progress

def params_to_vector(d:dict):
    g,m,c = d['geometry'], d['motion'], d['health']
    return [ g['n'],g['i'],g['r'],g['d'],g['e'], m['t'],m['k'],m['w'] ] + [c[k] for k in HEALTH]

def vector_to_params(v):
    return {'geometry':dict(zip(GEOMETRY,v[:NUM_GEOMETRY])),
            'motion':dict(zip(MOTION,v[NUM_GEOMETRY:NUM_GEOMETRY+NUM_MOTION])),
            'health':dict(zip(HEALTH, v[-NUM_STATES * NUM_STATES:]))
           }