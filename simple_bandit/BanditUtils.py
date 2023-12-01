###################################################################################################
###################################################################################################
# imports
###################################################################################################
import json
import numpy as np

#####################################################################################################
#####################################################################################################
# calculate intervals - get the time intervals the mulit-arm bandit will be choosing a lc to observe
####################################################################################################
def get_intervals(init_time, time_step):
    pass
    # given an initial time and time step, calculate the intervals (start_time, end_time)
    # return a list of intervals for RunBandit to use
    # the first interval (at index 0) should be from (- infinity, largest time the initial obs were taken)