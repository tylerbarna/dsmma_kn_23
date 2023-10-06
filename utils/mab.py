''' 
functions for implementing the multi-arm bandit within analysis_script.py
'''

import json
import numpy as np


def mask_lightcurve(mask, lc):
    '''
    Masks the true lightcurve so only the observed time-points have values.

    Assumptions: 
    - len(mask) == max len(lc). Since len(mask) = max(time), this should be true
    - all lc have key value 'ztfg'

    ## Q:  How should the timepoints be masked? Currently, they become [0, 0, 0]
    ## Q:  Should lc be 'cut' so the most current time point is the last time point?
    ## Q:  Is it ok to just have one file be overwritten? Will models run sequentially or parallel?

    Args:
    - mask (list): list holding the timepoints where the object was observed {1} or not observed {0}
    - lc (json): the true observations for the object in json format

    Returns:
    - No returns, saves masked lc to file 'lc_masked.json'
    '''

    for i in range(len(lc['ztfg'])):
        if mask[i] == 0:
            lc['ztfg'][i] = [0, 0, 0]

    masked_file = open("lc_masked.json", "w")
    json.dump(lc, masked_file, indent = 6)
    masked_file.close()