''' 
functions for implementing the multi-arm bandit within mab_analysis_script.py
'''

import json
import numpy as np

def get_reward():
    pass

def create_mask():
    pass

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
    - No returns, saves masked lc to file 'lc_masked_{model_n}.json'
    '''

    for k in lc.keys():
            del_count = 0

            for i in range(len(lc[k])):
                if mask[k][i] == 0:
                    del lc[k][i - del_count]
                    del_count += 1

    masked_file = open(f"lc_masked_{model_n}.json", "w")
    json.dump(lc, masked_file, indent = 6)
    masked_file.close()