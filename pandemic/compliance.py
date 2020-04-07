from pandemic.conventions import SYMPTOMATIC, POSITIVE
import numpy as np

def destinations(status, time_of_day, home_locations, work_locations, compliant=True ):
    return [ h if time_of_day >= 0.5 or ( compliant and s in [SYMPTOMATIC, POSITIVE] ) else w for s,h,w in zip( status, home_locations, work_locations) ]
