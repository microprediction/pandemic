from pandemic.conventions import SYMPTOMATIC, POSITIVE

def destinations(status, time_of_day, home_locations, work_locations, compliant=True ):
    """ If sick, stay home! """  # TODO: cohorts for compliance rather than all or nothing.
    return [ h if time_of_day >= 0.5 or ( compliant and s in [SYMPTOMATIC, POSITIVE] ) else w for s,h,w in zip( status, home_locations, work_locations) ]
