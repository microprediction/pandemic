from pandemic.estimation import params_to_vector, vector_to_params
from pandemic.conventions import EXAMPLE_PARAMETERS
from deepdiff import DeepDiff

def test_flatten():
    prms_in = EXAMPLE_PARAMETERS.copy()
    v        = params_to_vector(prms_in)
    prms_out = vector_to_params(v)
    d        =  DeepDiff(prms_in, prms_out, ignore_order=True)
    print(d)
