from pandemic.conventions import HEALTH_DESCRIPTIONS, HEALTH, STATES, VULNERABLE, INFECTED, SYMPTOMATIC, RECOVERED, DECEASED, POSITIVE
from pandemic.util import flatten
import numpy as np


def contact_progression(status, health_params, exposed):
    """ Sometimes exposure leads to infection
    :param exposed:         [ boolean ]
    :return: new status
    """
    return [INFECTED if x and s == VULNERABLE and np.random.randn() < health_params['vi'] else s for s, x in zip(status, exposed)]


def individual_progression(status, health_params, day_fraction):
    """
        :param status         [ int ]     Vector of status
        :param health_params  dict of illness transition parameters
        :param day_fraction   float       Between 0 and 1
    """

    def symptom_emergence(status, p_symptomatic):
        return [ SYMPTOMATIC if s == INFECTED and np.random.rand() < day_fraction*p_symptomatic else s for s in status ]

    def recovery(status, cohort, p_recovery):
        return [RECOVERED if s == cohort and np.random.rand() < day_fraction*p_recovery else s for s in status]

    def death(status, cohort, p_death):
        return [DECEASED if s == cohort and np.random.rand() < day_fraction * p_death else s for s in status]

    def random_testing(status, p_asymptomatic):
        return [POSITIVE if s==INFECTED and np.random.rand() < day_fraction*p_asymptomatic else s for s in status]

    def testing(status, p_symptomatic):
        return [POSITIVE if s==SYMPTOMATIC and np.random.rand() < day_fraction * p_symptomatic else s for s in status]

    status = symptom_emergence(status, p_symptomatic=health_params['is'])
    status = random_testing( status=status, p_asymptomatic=health_params['ip'])
    status = testing(status=status, p_symptomatic=health_params['sp'])
    status = recovery(status, cohort=INFECTED, p_recovery=health_params['ir'])
    status = recovery(status, cohort=POSITIVE, p_recovery=health_params['pr'])
    status = recovery(status, cohort=SYMPTOMATIC, p_recovery=health_params['sr'])
    status = death(status, cohort=INFECTED, p_death=health_params['id'])
    status = death(status, cohort=POSITIVE, p_death=health_params['pd'])
    status = death(status, cohort=SYMPTOMATIC, p_death=health_params['sd'])

    return status


# Aside: useful for tests against matrix status updates ...
CANONICAL_ILLNESS_ORDERING   = flatten([[s1 + s2 for s1 in STATES if s1 + s2 in HEALTH_DESCRIPTIONS.keys()] for s2 in STATES])  # Canonical ordering of non-zero transition parameters