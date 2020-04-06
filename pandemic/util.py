import itertools

# Utils that have nothing to do with the model

def flatten(list_of_list):
    return list(itertools.chain.from_iterable(list_of_list))

def chunks(l, n):
    n = max(1, n)
    return list(l[i:i+n] for i in range(0, len(l), n))