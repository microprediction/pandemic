from collections import Counter
from pandemic.conventions import STATES, POSITIVE, INFECTED, RECOVERED, DECEASED
from geohash import encode

# ---------------------------------------------------------
#    Functionals of position, status and other variables
# ---------------------------------------------------------


def cases_and_deaths(status):
    sc = status_counts(status)
    cases  = sc[POSITIVE]+sc[RECOVERED]+sc[DECEASED]
    deaths = sc[DECEASED]
    return [ cases, deaths ]


def status_counts(status, **ignore_other_kwargs):
    counts = Counter(status)
    return [ counts[k] for k,_ in enumerate(STATES) ]

def collision_count(positions, status, precision, criteria=None):
    if criteria == None:
        criteria = lambda pos, status: True
    geohashed = [encode(pos[0], pos[1], precision=precision) for pos, s in zip(positions, status) if criteria(pos,s)]
    return len(geohashed) - len(set(geohashed))


