# Entry point for command line

from pandemic.example_parameters import BASELINES, LARGE_TOWN
from pandemic.conventions import DESCRIPTIONS, CATEGORIES
from pandemic.simulation import simulate
import  matplotlib.pyplot as plt
import sys

def modifier( category, param, factor, baseline=None):
    # Returns modified town and description of how it was modified
    params = baseline or LARGE_TOWN
    cat_params = params[category]
    cat_params[param] = cat_params[param]*factor
    params[category] = cat_params
    description = (DESCRIPTIONS[category][param] + ' multiplied by ' + str(factor))
    return params, description

def modify_and_run(baseline, triples):
    # python3 cmd.py geometry n 20000 health vi 0.5
    params = BASELINES[baseline]
    descriptions = list()
    n = len(triples)
    assert n % 3 ==0, 'Expecting triples of command line parameters '
    num = int(n/3)
    print(num)
    for k in range(num):
        category = triples[3 * k].lower()
        param    = triples[3 * k+1].lower()
        assert category in CATEGORIES
        assert param in list(DESCRIPTIONS[category].keys())
        factor   = float(triples[3*k+2])
        params, desc = modifier( category=category, param=param, factor=factor, baseline=params )
        descriptions.append(desc)
    simulate(params=params, plt=plt, xlabel=','.join(descriptions))

if __name__=="__main__":
    modify_and_run(baseline=sys.argv[1],triples=sys.argv[2:])