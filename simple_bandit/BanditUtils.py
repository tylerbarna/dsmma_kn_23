###################################################################################################
###################################################################################################
# imports
###################################################################################################
import json
import numpy as np

import os
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

        
def lc_analysis_test(lc, model, prior, outdir, label):
    
    kn = {
    "luminosity_distance": 43.86392473725086,
    "beta": 3.7299544604416166,
    "log10_kappa_r": 0.4597805423526466,
    "KNtimeshift": -0.0215943641959759,
    "log10_vej": -1.406799995564421,
    "log10_mej": -2.9722156205901293,
    "Ebv": 0.3061284522346548,
    "log_likelihood": 10,
    "log_prior": -9.717849136485976,
    "log_bayes_factor": 0.1,
    "Best fit index": 3054,
    "Magnitudes": {
        "ztfg": [
            23.02626560507143,
            20.521257796549563,
            19.66669767644992,
            18.93668416756229,
            18.419908820983537,
            18.08003077765553,
        ],
        "bestfit_sample_times": [
            0.1,
            0.6,
            1.1,
            1.6,
            2.1,
            2.6,
            3.1
        ]
        }      
    }

    other = {
    "luminosity_distance": 43.86392473725086,
    "beta": 3.7299544604416166,
    "log10_kappa_r": 0.4597805423526466,
    "KNtimeshift": -0.0215943641959759,
    "log10_vej": -1.406799995564421,
    "log10_mej": -2.9722156205901293,
    "Ebv": 0.3061284522346548,
    "log_likelihood": 1,
    "log_prior": -9.717849136485976,
    "log_bayes_factor": -10,
    "Best fit index": 3054,
    "Magnitudes": {
        "ztfg": [
            23.02626560507143,
            20.521257796549563,
            19.66669767644992,
            18.93668416756229,
            18.419908820983537,
            18.08003077765553,
        ],
        "bestfit_sample_times": [
            0.1,
            0.6,
            1.1,
            1.6,
            2.1,
            2.6,
            3.1
        ]
        }      
    }

    lc_file = open(lc)
    lc_og = json.load(lc_file)
    lc_file.close()

    # print(lc_og['ztfg'][1]) #####################################################################
    if lc_og['ztfg'][1][0] % 2 == 0:
        value = kn
    else:
        value = other
    
    # get outdir and name of file
    file_name = os.path.join(outdir, label + "_bestfit.json")

    # the json file to save the output data   
    save_file = open(file_name, "w")  
    json.dump(value, save_file, indent = 6)  
    save_file.close()

    return file_name

    
