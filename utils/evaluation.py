'''
functions for evaluating the results of fitting
'''

import json
import os
import pandas as pd
import numpy as np

from utils.injections import get_parameters

from utils.lightcurves import read_lightcurve

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
        
    best_fit_params = best_fit_params_json.copy() ## define best fit params as best_fit_params_json with the 'Magnitudes' key removed
    best_fit_lightcurve_dict = best_fit_params.pop('Magnitudes') ## this pulls double duty of both removing the 'Magnitudes' key and returning the lightcurve dict 
    best_fit_lightcurve = pd.DataFrame.from_dict(best_fit_lightcurve_dict) ## can handle multiple filters
    
    return best_fit_params, best_fit_lightcurve

def calculate_lightcurve_residual(lightcurve_df, best_fit_lightcurve_df):
    '''
    Calculates the residual between the lightcurve and the best fit lightcurve
    
    Args:
    - lightcurve_df (pd.DataFrame): dataframe of lightcurve with associated times
    - best_fit_lightcurve_df (pd.DataFrame): dataframe of best fit lightcurve with associated times
    
    Returns:
    - lightcurve_residual (pd.DataFrame): dataframe of lightcurve residual with associated times
    
    Todo:
    TEST THIS FUNCTION
    '''
    
    time_cutoff = best_fit_lightcurve_df['bestfit_sample_times'].max() ## get the maximum time of the best fit lightcurve
    lighcurve_df = lightcurve_df[lightcurve_df['sample_times'] <= time_cutoff]
    lightcurve_residual = 0 ## initialize lightcurve residual
    for filter in lightcurve_df.keys():
        ## residual given by (lightcurve - best_fit_lightcurve)^2 / lightcurve_err
        filter_residual = np.array((lightcurve_df[filter] - best_fit_lightcurve_df[filter])**2/lightcurve_df[f'{filter}_err']) ## calculate the residual for each filter. may want to have an except in the event that there is no error
        
        lightcurve_residual += np.nansum((filter_residual), where=filter_residual!=np.inf) / len(np.isreal(lightcurve_df[filter])) ## sum the residuals for each filter and normalize by the number of samples. Accounts for the fact that the number of samples may be different for each filter and that there may be inf values in the residuals

    return lightcurve_residual

def get_model_name(best_fit_json, **kwargs):
    '''
    Gets the model name from the best fit json file
    
    Args:
    - best_fit_json (str): path to best fit json file
    
    Returns:
    - model_name (str): model name
    '''
    model_name = os.path.basename(best_fit_json).split(kwargs.get('file_sep','_'))[kwargs.get('model_idx',4)] ## get model name from best fit json. Assumes that the model name is the 4th item in the filename, separated by underscores, but these can be changed with kwargs
    
    return model_name

def evaluate_fits_by_residuals(lightcurve_json, best_fit_json_list, **kwargs):
    '''
    Evaluates the fit between the lightcurve and the best fit lightcurve
    
    Args:
    - lightcurve_json (str): path to lightcurve json file
    - best_fit_json_list (list): list of paths to best fit json files
    
    Returns:
    - fit_eval (dict): dictionary of fit evaluation metrics
    '''
    lightcurve_df = read_lightcurve(lightcurve_json) ## read in lightcurve
    models = [get_model_name(best_fit_json) for best_fit_json in best_fit_json_list] 
    best_fit_lightcurve_df_list = [read_best_fit_params(best_fit_json)[1] for best_fit_json in best_fit_json_list] ## read in best fit lightcurves
    
    residuals_dict = {model: calculate_lightcurve_residual(lightcurve_df, best_fit_lightcurve_df) for model, best_fit_lightcurve_df in zip(models, best_fit_lightcurve_df_list)} ## calculate residuals for each model
    
    residuals_dict = {model: residuals_dict[model] for model in sorted(residuals_dict, key=residuals_dict.get)} ## order residuals from smallest to largest. the model with the smallest residual can be considered to be the best fit
    
    return residuals_dict

    
def evaluate_fits_by_likelihood(best_fit_json_list, target_model='Me2017', **kwargs):
    '''
    compares the likelihoods of the best fit json files
    
    Args:
    - best_fit_json_list (list): list of paths to best fit json files
    - target_model (str): model to compare to (default='Me2017')
    
    Returns:
    - fit_eval (dict): dictionary of fit evaluation based on difference in likelihoods
    '''
    models = [get_model_name(best_fit_json) for best_fit_json in best_fit_json_list] 
    best_fit_params_list = [read_best_fit_params(best_fit_json)[0] for best_fit_json in best_fit_json_list] ## read in best fit parameters
    best_fit_likelihoods = [best_fit_params['log_likelihood'] for best_fit_params in best_fit_params_list] ## get likelihoods for each model
    best_fit_likelihoods_dict = {model: best_fit_likelihood for model, best_fit_likelihood in zip(models, best_fit_likelihoods)} ## convert to dictionary
    likelihood_diff_dict = {model: best_fit_likelihoods_dict[target_model] - best_fit_likelihoods_dict[model] for model in models} ## calculate the difference in likelihood between the target model and each model
    fit_eval = {model: likelihood_diff_dict[model] for model in sorted(likelihood_diff_dict, key=likelihood_diff_dict.get, reverse=True)} ## the model with the largest difference in likelihood can be considered to be the best fit
    
    return fit_eval
