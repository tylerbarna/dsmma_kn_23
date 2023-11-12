'''
functions for evaluating the results of fitting
'''
import argparse
import glob
from itertools import groupby
import json
import os
import pandas as pd
import numpy as np
import warnings
from multiprocessing import Pool, cpu_count
from functools import partial

from injections import get_parameters
warnings.simplefilter(action='ignore', category=FutureWarning)
from lightcurves import read_lightcurve
from misc import suppress_print, strtime

def read_best_fit_params(json_path, **kwargs):
    '''
    Reads in a best fit parameters json and returns a dictionary of the best fit parameters as well as a pandas dataframe of the best fit lightcurve with associated times
    
    Args:
    - json_path (str): path to best fit file
    
    Returns:
    - best_fit_params (dict): dictionary of best fit parameters
    - best_fit_lightcurve (pd.DataFrame): dataframe of best fit lightcurve with associated times
    '''
    best_fit_lightcurve_type = kwargs.get('best_fit_lightcurve_type', 'pandas') ## default to pandas but can return a dict if desired
    with open(json_path) as f:
        best_fit_params_json = json.load(f)
        
    best_fit_params = best_fit_params_json.copy() ## define best fit params as best_fit_params_json with the 'Magnitudes' key removed
    best_fit_lightcurve_dict = best_fit_params.pop('Magnitudes') ## this pulls double duty of both removing the 'Magnitudes' key and returning the lightcurve dict 
    if best_fit_lightcurve_type == 'pandas':
        best_fit_lightcurve = pd.DataFrame.from_dict(best_fit_lightcurve_dict) ## can handle multiple filters
    elif best_fit_lightcurve_type == 'dict':
        best_fit_lightcurve = best_fit_lightcurve_dict
    
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
    lightcurve_df = lightcurve_df[lightcurve_df['sample_times'] <= time_cutoff]
    lightcurve_residual = 0 ## initialize lightcurve residual
    for filter in ['ztfg','ztfr','ztfi']: ##    TO-DO: make this more general so that it can handle any filter
        if filter == 'sample_times':
            continue
        elif filter not in lightcurve_df.keys():
            continue
        ## residual given by (lightcurve - best_fit_lightcurve)^2 / lightcurve_err
        try:
            ## get indices where the err is nan or inf
            nondetection_indices = np.where(np.isnan(lightcurve_df[f'{filter}_err']) | np.isinf(lightcurve_df[f'{filter}_err']))[0]
            ## now only keep the indices of the filter where the err is not nan or inf
            lightcurve_df = lightcurve_df[~lightcurve_df.index.isin(nondetection_indices)]
            best_fit_lightcurve_df = best_fit_lightcurve_df[~best_fit_lightcurve_df.index.isin(nondetection_indices)]
            filter_residual = np.array((lightcurve_df[filter] - best_fit_lightcurve_df[filter])**2/lightcurve_df[f'{filter}_err']) ## calculate the residual for each filter. may want to have an except in the event that there is no error
            if len(np.isreal(lightcurve_df[filter])) == 0:
                continue
            else:
                lightcurve_residual += np.nansum(filter_residual[~np.isinf(filter_residual)]) / len(np.isreal(lightcurve_df[filter])) ## sum the residuals for each filter and normalize by the number of samples. Accounts for the fact that the number of samples may be different for each filter and that there may be inf values in the residuals
        except Exception as e:
             ## TO-DO: make it so you don't have to have this except (due to above)
            print('Residual Calculation Error: ', e)
            continue

    return lightcurve_residual

def get_model_name(best_fit_json, **kwargs):
    '''
    Gets the model name from the best fit json file
    
    Args:
    - best_fit_json (str): path to best fit json file
    
    Returns:
    - model_name (str): model name
    '''
    # print('gmn bfj',best_fit_json)
    # print('gmn ospbn',os.path.basename(best_fit_json).split(kwargs.get('file_sep','_')))
    model_name = os.path.basename(best_fit_json).split(kwargs.get('file_sep','_'))[kwargs.get('model_idx',4)] ## get model name from best fit json. Assumes that the model name is the 4th item in the filename, separated by underscores, but these can be changed with kwargs
    
    return model_name

def get_lightcurve_name(lightcurve_json, **kwargs):
    '''
    Retrieves the lightcurve name from the lightcurve json file
    '''
    file_seperator = kwargs.get('file_sep','_') ## seperator between items in filename
    name_idx = kwargs.get('name_idx', 1) ## position of lightcurve name in lightcurve filename, the default is 1 (eg lc_Me2017_00000). This means that the lightcurve model is this idx and the lightcurve label is idx_idx+1m
    lightcurve_name = os.path.basename(lightcurve_json).split(file_seperator)[name_idx] + '_' + os.path.basename(lightcurve_json).split(file_seperator)[name_idx+1]
    ## remove .json from the end of the lightcurve name
    lightcurve_name = lightcurve_name.split('.')[0]
    return lightcurve_name

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

def create_fit_series(lightcurve_path, best_fit_json_path, **kwargs):
    '''
    Creates a series for a specific lightcurve and best fit json file, with the following columns:
    
    - lightcurve (str): lightcurve name (eg lc_Me2017_00000)
    - true_model (str): true model name (eg Me2017)
    - lightcurve_path (str): path to lightcurve
    - fit_model (str): model name of best fit (eg Me2017)
    - fit_path (str): path to best fit json file
    - t_max (float): time of most recent observed data point
    - *residual (float): residual between lightcurve and best fit lightcurve
    - *odds_ratio (float): odds ratio of the best fit model compared to true model 
    * (note: the current implementation of these functions calculates them for a list of best fit json files, so these columns will need to turn them from a list to a float)
    - best_fit_params (dict): dictionary of best fit parameters (dependent on specific fit model)
    
    Args:
    - lightcurve_path (str): path to lightcurve
    - best_fit_json_path (str): path to best fit json file
    
    Returns:
    - fit_series (pd.Series): series of fit evaluation metrics
    '''
    file_seperator = kwargs.get('file_sep','_') ## seperator between items in filename
    lc_model_idx = kwargs.get('lc_model_idx', 1) ## position of lightcurve model in lightcurve filename, the default is 1 (eg lc_Me2017_00000). This means that the lightcurve model is this idx and the lightcurve label is idx_idx+1
    true_model = os.path.basename(lightcurve_path).split(file_seperator)[lc_model_idx]
    lightcurve_name = get_lightcurve_name(lightcurve_path, **kwargs)
    tmax_idx = kwargs.get('tmax_idx', 6) ## position of tmax in lightcurve filename, the default is 3 (eg lc_Me2017_00000_fit_Me2017_tmax_3). This means that the tmax is this idx
    best_fit_params, best_fit_lightcurve_df = read_best_fit_params(best_fit_json_path) ## read in best fit parameters
    ## from best_fit_params, get the log_likelihood
    log_likelihood = best_fit_params['log_likelihood']
    log_prior = best_fit_params['log_prior']
    log_bayes_factor = best_fit_params['log_bayes_factor']
    # log_bayes_factor = best_fit_params['log_bayes_factor'] ## for when the log_bayes_factor is added to the set of best fit parameters
    target_model = kwargs.get('target_model', 'Me2017') ## model to compare to
    lightcurve_df = read_lightcurve(lightcurve_path) ## read in lightcurve
    # print(lightcurve_df['sample_times'])
    ## get a kwarg of injection_path, but if it isn't provided, set it to the path of the lightcurve, but with the 'lc' replaced with 'inj'
    injection_path = kwargs.get('injection_path', lightcurve_path.replace('lc','inj'))
    
    
    series = pd.Series(dtype='float64') ## initialize series
    series['lightcurve'] = lightcurve_name
    series['true_model'] = true_model
    series['lightcurve_path'] = lightcurve_path
    series['true_params'] = get_parameters(injection_path)
    series['true_lightcurve'] = lightcurve_df.to_dict() 
    series['fit_model'] = get_model_name(best_fit_json_path, **kwargs)
    series['fit_path'] = best_fit_json_path
    series['t_max'] = float(os.path.basename(best_fit_json_path).split(file_seperator)[tmax_idx]) ## get tmax from lightcurve path
    series['residual'] = calculate_lightcurve_residual(lightcurve_df, best_fit_lightcurve_df) 
    #series['odds_ratio'] = evaluate_fits_by_likelihood([best_fit_json_path], target_model=target_model)[0] ## need to rethink how this works
    series['log_likelihood'] = log_likelihood
    series['log_prior'] = log_prior
    series['log_bayes_factor'] = log_bayes_factor
    series['best_fit_params'] = best_fit_params
    series['best_fit_lightcurve'] = best_fit_lightcurve_df.to_dict()
    
    ## note: should I also have it store the best fit lightcurve and the lightcurve as dictionaries? Might be useful for plotting
    
    return series
    
def associate_lightcurves_and_fits(lightcurve_paths, best_fit_json_paths, **kwargs):
    '''
    Creates a dictionary where each key is a lightcurve path and the list is a list of lists, with each sublist representing a time step
    
    Args:
    - lightcurve_paths (list): list of lightcurve paths
    - best_fit_json_paths (list): list of best fit json paths
    
    Returns:
    - lightcurve_fit_dict (dict): dictionary of lightcurve paths and associated best fit json paths
    '''
    file_seperator = kwargs.get('file_sep','_') ## seperator between items in filename
    tmax_idx = kwargs.get('tmax_idx', 6) ## position of tmax in lightcurve filename, the default is 6 (eg lc_Me2017_00000_fit_Me2017_tmax_3).
    lightcurve_fit_dict = {}
    for lightcurve_path in lightcurve_paths:
        lightcurve_fit_dict[lightcurve_path] = []
        for best_fit_json_path in best_fit_json_paths:
            lightcurve_name = get_lightcurve_name(lightcurve_path, **kwargs).split('.')[0] ## to remove the json
            best_fit_lightcurve_name = get_lightcurve_name(best_fit_json_path, **kwargs)
            if lightcurve_name == best_fit_lightcurve_name:
                lightcurve_fit_dict[lightcurve_path].append(best_fit_json_path)
        lightcurve_fit_dict[lightcurve_path] = sorted(lightcurve_fit_dict[lightcurve_path], key=lambda x: float(os.path.basename(x).split(file_seperator)[tmax_idx])) ## sort the list of best fit jsons by tmax
        lightcurve_fit_dict[lightcurve_path] = [list(g) for _, g in groupby(lightcurve_fit_dict[lightcurve_path], key=lambda x: float(os.path.basename(x).split(file_seperator)[tmax_idx]))] ## splitting them into sublists based on tmax
        
    return lightcurve_fit_dict
            


import pandas as pd
from multiprocessing import Pool, cpu_count
from functools import partial
from time import time as strtime

import pandas as pd
from multiprocessing import Pool, cpu_count
from functools import partial
from time import time as strtime

def create_dataframe(lightcurve_paths, best_fit_json_paths, parallel=False, **kwargs):
    '''
    Creates a dataframe of fit evaluation metrics
    
    Args:
    - lightcurve_paths (list): list of lightcurve paths
    - best_fit_json_paths (list): list of best fit json paths
    - parallel (bool): optional argument to enable parallel processing (default is False)
    
    Returns:
    - fit_df (pd.DataFrame): dataframe of fit evaluation metrics
    '''
    def process_lightcurve(lightcurve_path, best_fit_json_list, **kwargs):
        fit_series_list = []
        for best_fit_json in best_fit_json_list:
            fit_series = create_fit_series(lightcurve_path, best_fit_json, **kwargs)
            fit_series_list.append(fit_series)
        return fit_series_list

    lightcurve_fit_dict = associate_lightcurves_and_fits(lightcurve_paths, best_fit_json_paths, **kwargs)
    fit_df = pd.DataFrame()
    print(f'[{strtime()}] Creating Dataframe')

    if parallel:
        num_processes = min(cpu_count(), len(lightcurve_paths))
        with Pool(num_processes) as pool:
            partial_process_lightcurve = partial(process_lightcurve, **kwargs)
            results = []

            for lightcurve_path in lightcurve_paths:
                print(f'[{strtime()}] Creating Dataframe items for {lightcurve_path}')
                for best_fit_json_list in lightcurve_fit_dict[lightcurve_path]:
                    async_result = pool.apply_async(partial_process_lightcurve, args=(lightcurve_path, best_fit_json_list))
                    results.append(async_result)

            pool.close()
            pool.join()

            for async_result in results:
                fit_series_list = async_result.get()
                for fit_series in fit_series_list:
                    fit_df = fit_df.append(fit_series, ignore_index=True)
    else:
        for lightcurve_path in lightcurve_paths:
            print(f'[{strtime()}] Creating Dataframe items for {lightcurve_path}')
            for best_fit_json_list in lightcurve_fit_dict[lightcurve_path]:
                for best_fit_json in best_fit_json_list:
                    fit_series = create_fit_series(lightcurve_path, best_fit_json, **kwargs)
                    fit_df = fit_df.append(fit_series, ignore_index=True)

    fit_df.sort_values(by=['lightcurve', 't_max', 'fit_model'], inplace=True)
    fit_df.reset_index(drop=True, inplace=True)

    return fit_df




def main():
    parser = argparse.ArgumentParser(description='Evaluate the results of fitting.')
    parser.add_argument('--lc-path', metavar='lightcurve_paths', type=str, 
                            help='paths to the lightcurve files')
    parser.add_argument('--fit-path', metavar='best_fit_json_paths', type=str, 
                            help='paths to the best fit json files')
    parser.add_argument('--output', metavar='output_csv',
                            help='path to the output csv file')
    parser.add_argument('--parallel', action='store_true', help='enable parallel processing')
    args = parser.parse_args()
    ## get all the lightcurve and best fit json paths
    lightcurve_paths = sorted(glob.glob(os.path.join(args.lc_path,'lc*.json')))
    ## get all *bestfit_params.json files from fits_expanse regardless of subdirectory depth
    best_fit_json_paths = sorted(glob.glob(os.path.join(args.fit_path,'**/*bestfit_params.json'),recursive=True)) ## note: this will only work on python 3.5+
    ## if output does not end in csv, add it
    args.output = args.output if args.output.endswith('.csv') else args.output + '.csv'
    fit_df = create_dataframe(lightcurve_paths, best_fit_json_paths, parallel=args.parallel)
    print(f'[{strtime()}] Dataframe creation complete')
    print(fit_df)
    fit_df.to_csv(args.output)
    
if __name__ == "__main__":
    main()