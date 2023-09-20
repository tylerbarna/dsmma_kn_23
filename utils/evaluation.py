'''
functions for evaluating the results of fitting
'''

import json
import os
import pandas as pd
import numpy as np


def read_best_fit_params(json_path):
    '''
    Reads in a best fit parameters json and returns a dictionary of the best fit parameters as well as a pandas dataframe of the best fit lightcurve with associated times
    
    Args:
    - json_path (str): path to best fit file
    
    Returns:
    - best_fit_params (dict): dictionary of best fit parameters
    - best_fit_lightcurve (pd.DataFrame): dataframe of best fit lightcurve with associated times
    '''
    
    with open(json_path) as f:
        best_fit_params_json = json.load(f)
        
    ## define best fit params as best_fit_params_json with the 'Magnitudes' key removed
    best_fit_params = best_fit_params_json.copy()
    best_fit_lightcurve_dict = best_fit_params.pop('Magnitudes') ## this pulls double duty of both removing the 'Magnitudes' key and returning the lightcurve dict 
    best_fit_lightcurve = pd.DataFrame.from_dict(best_fit_lightcurve_dict) ## can handle multiple filters
    
    return best_fit_params, best_fit_lightcurve