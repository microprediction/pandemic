from pandemic.surrogate import int_to_cube, cube_to_int, free_param_percentiles, Surrogate
from pandemic.example_parameters import LARGE_TOWN
import copy

def test_embedding():
    v = [0.6,0.2,0.1]
    h = cube_to_int(v)
    v1 = int_to_cube(h, dim=len(v))
    assert( all( [ abs(v1_-v_)<1e-3 for v1_, v_ in zip(v,v1)]))


def test_free_param_percentiles():
    params = copy.deepcopy( LARGE_TOWN )
    params['motion']['w']=6.13
    free = free_param_percentiles(params=params,baseline='large_town')
    assert len(free)==3
    if params['motion']['w']> LARGE_TOWN['motion']['w']:
        assert free[1]>0.5

