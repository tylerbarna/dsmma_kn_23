''' 
functions for implementing the multi-arm bandit within analysis_script.py
'''

import json
import numpy as np


def mask_lightcurve(mask, lc, model_n):
    '''
    Masks the true lightcurve so only the observed time-points have values.

    Assumptions: 
    - len(mask) == max len(lc). Since len(mask) = max(time), this should be true

    Args:
    - mask (dict): dictionary holding the timepoints where the object was observed (1) or not observed (0) {'ztfg': [1 1 0 1]}
    - lc (json): the true observations for the object in json format
    - model_n: name of the lightcurve model

    Returns:
    - No returns, saves masked lc to file 'lc_masked.json'
    '''

    for k in lc.values():
        for i in range(len(lc[k])):
            if mask[k][i] == 0:
                del lc[k][i]

    masked_file = open(f"lc_masked{model_n}.json", "w")   ## incorporate name of the lightcurve
    json.dump(lc, masked_file, indent = 6)
    masked_file.close()