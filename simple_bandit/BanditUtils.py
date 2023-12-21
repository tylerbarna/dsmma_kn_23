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
def get_intervals(init_time, time_step, n_steps):
    '''
    Generate intervals: (- infinity, init_time), 
                        (init_time, init_time + time_step), 
                        (init_time + time_step, init_time + time_step * 2),
                           ...,
                        (init_time + time_step * (n_steps), init_time + time_step * (n_steps + 1))
                           
    Args: init_time (float) - the latest time observation for all the candidate objects
          time_step (float) - the length of time you want each observation interval to be
          n_steps (int) - the number of intervals you wants
    '''
    intervals = [(- np.Infinity, init_time)]

    for j in range(n_steps):
    
        new_i = init_time + (time_step)

        intervals.append((init_time, new_i))

        init_time = new_i

    return intervals

        
    

    
