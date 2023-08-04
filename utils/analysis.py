'''
functions for analysis of generated lightcurves
'''

import multiprocessing
import numpy as np
import os
import pandas as pd
import time

from argparse import Namespace

from functools import wraps

from nmma.em import analysis

from utils.misc import strtime, suppress_print


def lightcurve_analysis(lightcurve_path, model, prior, outdir, label, tmax=None, threading=False, **kwargs):
    '''
    Uses nmma to analyse a given lightcurve against a specific model and prior
    
    Args:
    - lightcurve_path (str): path to lightcurve file
    - model (str): model to use (must exist in nmma)
    - prior (str): path to prior file (must match model)
    - outdir (str): path to output directory (will be created if it doesn't exist)
    - label (str): label for analysis files
    - tmax (float): maximum time to consider in analysis (default=None, which means use all data)
    - threading (bool): whether to use threading (default=False). If True, will use multiprocessing.Process to run analysis in parallel
    
    Returns:
    - results_path (str): path to results file
    - bestfit_path (str): path to bestfit file
    '''
    assert os.path.exists(lightcurve_path), 'lightcurve file {} does not exist'.format(lightcurve_path)
    os.makedirs(outdir, exist_ok=True)
    
    if not tmax:
        try:
            lightcurve_df = pd.read_json(lightcurve_path)
            # print('lightcurve_df ',lightcurve_df)
            tmax = lightcurve_df.max()[0][0]+0.1 - lightcurve_df.min()[0][0] ## should return the last time in the lightcurve
        except:
            tmax = 21 ## nmma might not like this 
    # print('tmax is {}'.format(tmax))
    
    args = Namespace(
        data=lightcurve_path,
        injection=None,
        model=model,
        prior=prior,
        label=label,
        trigger_time=0.1, ## may tweak this
        outdir=outdir,
        interpolation_type="sklearn_gp",
        svd_path="svdmodels",
        tmin=0.1,
        tmax=tmax,
        dt=0.5,
        log_space_time=False,
        photometric_error_budget=0.1,
        soft_init=False,
        bestfit=True,
        svd_mag_ncoeff=10,
        svd_lbol_ncoeff=10,
        filters="sdssu",
        Ebv_max=0.0,
        grb_resolution=5,
        jet_type=0,
        error_budget="1",
        sampler="pymultinest",
        cpus=1,
        nlive=512,
        seed=42,
        remove_nondetections=True,
        detection_limit=None,
        with_grb_injection=False,
        prompt_collapse=False,
        ztf_sampling=False,
        ztf_uncertainties=True,
        ztf_ToO=None,
        train_stats=False,
        rubin_ToO=False,
        rubin_ToO_type=None,
        xlim="0,21",
        ylim="22,16",
        generation_seed=42,
        plot=True,
        bilby_zero_likelihood_mode=False,
        photometry_augmentation=False,
        photometry_augmentation_seed=0,
        photometry_augmentation_N_points=10,
        photometry_augmentation_filters=None,
        photometry_augmentation_times=None,
        conditional_gaussian_prior_thetaObs=False,
        conditional_gaussian_prior_N_sigma=1,
        sample_over_Hubble=False,
        sampler_kwargs="{}",
        reactive_sampling=False,
        verbose=False,
    ) 
    
    # @suppress_print
    def analysis_main(args):
        analysis.main(args)
        
    if threading:
        print(f'running {label} in parallel')
        multiprocessing.freeze_support()
        process = multiprocessing.Process(target=analysis_main, args=(args,))
        if 'pool' in kwargs:
            kwargs.pool.apply_async(process.start())
        process.start()
    else:
        analysis_main(args)
    
    
    results_path = os.path.join(outdir, label + "_result.json")
    bestfit_path = os.path.join(outdir, label + "_bestfit.json")
    return results_path, bestfit_path

def timestep_lightcurve_analysis(lightcurve_path, model, prior, outdir, label=None, tmax_array=None, threading=True, **kwargs):
    '''
    wrapper for lightcurve_analysis that runs multiple analyses for a given lightcurve and model with different tmax values
    
    Args:
    - lightcurve_path (str): path to lightcurve file
    - model (str): model to use (must exist in nmma)
    - prior (str): path to prior file (must match model)
    - outdir (str): path to root output directory (will be created if it doesn't exist). A subdirectory for the specific object will be created if it doesn't exist
    - label (str): label for analysis files (a time value will be appended to this). If None, will use the lightcurve filename
    - tmax_array (array): array of tmax values to use in analysis (default=None, which imposes a two day cadence from 3 to 20 days)
    - threading (bool): whether to use threading (default=True). If True, will use multiprocessing.Process to run analysis in parallel
    
    Returns:
    - results_paths (list): list of paths to results files for a given lightcurve and model
    - bestfit_paths (list): list of paths to bestfit files for a given lightcurve and model
    '''
    
    assert os.path.exists(lightcurve_path), 'lightcurve file {} does not exist'.format(lightcurve_path)
    lightcurve_label = os.path.basename(lightcurve_path).split('.')[0]
    lighcurve_outdir = os.path.join(outdir, lightcurve_label)
    model_outdir = os.path.join(lighcurve_outdir, model) ## so directory structure will be {outdir}/{lightcurve_label}/{model}/
    os.makedirs(model_outdir, exist_ok=True)
    fit_label = lightcurve_label + '_fit_' + model if not label else label
    
    if tmax_array==None:
        try:
            lightcurve_df = pd.read_json(lightcurve_path)
            tmax = lightcurve_df.max()[0][0] - lightcurve_df.min()[0][0] ## should return the last time in the lightcurve
            tmax_array = np.arange(3.1,tmax+0.1,2)
        except:
            tmax_array = np.arange(3.1,20.1,2) ## nmma might not like this 
    
    results_paths = []
    bestfit_paths = []
    for tmax in tmax_array:
        tmax_label = fit_label + '_tmax_' + str(round(tmax,0)).zfill(2) ## imposes a label of the format 'lc_{true_model}_{idx}_fit_{model}_tmax_{tmax}'
        if os.path.exists(os.path.join(model_outdir, tmax_label + '_result.json')):
            print(f'{tmax_label} has already been fit, skipping')
            continue
        else:
            try:
                results_path, bestfit_path = lightcurve_analysis(lightcurve_path, model, prior, model_outdir, label=tmax_label, tmax=tmax, threading=threading, **kwargs)
                results_paths.append(results_path)
                bestfit_paths.append(bestfit_path)
            except:
                print(f'analysis of {tmax_label} failed, skipping')
                continue
    return results_paths, bestfit_paths

def check_completion(result_paths, t0, timeout=71.9):
    '''
    checks for truthiness of all json files existing in output directory
    
    args:
    - result_paths (list): list of the expected lightcurve result paths (including relative path)
    - t0 (time object): time of trigger (assign time.time() at start of analysis)
    - timeout (float): time in hours to wait until returning False even with incomplete analysis
    
    returns:
    - completion_status (bool): whether all lightcurves have been analysed
    - completed_analyses (array): array of lightcurve labels that have been analysed
    '''
    
    total_analyses = len(result_paths)
    analysis_status = np.array([os.path.exists(result_file) for result_file in result_paths], dtype=np.bool)
    completed_analyses = np.array(result_paths)[analysis_status]
    completed_analyses_count = np.sum(analysis_status)
    completion_status = completed_analyses_count == total_analyses
    
    current_time = strtime()
    t1 = time.time()
    hours_elapsed = round((t1 - t0) / 3600, 2)
    estimated_remaining_time = round((hours_elapsed / completed_analyses_count) * (total_analyses - completed_analyses_count),2)
    
    if hours_elapsed > timeout:
        print(f'[{current_time}] Analysis timed out with {total_analyses - completed_analyses_count} fits left, exiting...')
        return True, completed_analyses
    elif completion_status:
        print(f'[{current_time}] All {total_analyses} analyses complete!')
        return True, completed_analyses
    else:
        print(f'[{current_time}] {completed_analyses_count}/{total_analyses} analyses complete, estimated time remaining: {str(estimated_remaining_time).zfill(5)} hours')
        if hours_elapsed + estimated_remaining_time > timeout:
            excess_time = round((hours_elapsed + estimated_remaining_time - timeout),2)
            print(f'[{current_time}] Warning: estimated time remaining exceeds timeout by {excess_time} hours')
        return False, completed_analyses
    