from pandemic.conventions import params_to_vector, vector_to_params
from deepdiff import DeepDiff
from pandemic.example_parameters import LARGE_TOWN

def test_flatten():
    prms_in  = LARGE_TOWN.copy()
    v        = params_to_vector(prms_in)
    prms_out = vector_to_params(v)
    d        =  DeepDiff(prms_in, prms_out, ignore_order=True)
    assert len(d)==0

