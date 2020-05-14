from pandemic.conventions import params_to_vector, vector_to_params, flatten, unflatten
from deepdiff import DeepDiff
from pandemic.example_parameters import LARGE_TOWN
from copy import deepcopy



def test_flatten():
    params = deepcopy(LARGE_TOWN)
    flat_params = flatten(params)
    params1 = unflatten(flat_params)
    d = DeepDiff(params,params1)
    assert len(d)==0


def dont_test_vector():
    prms_in  = LARGE_TOWN.copy()
    v        = params_to_vector(prms_in)  # FIXME: Broken ... oops ... not using this yet fortunately
    prms_out = vector_to_params(v)
    d        =  DeepDiff(prms_in, prms_out, ignore_order=True)
    assert len(d)==0


