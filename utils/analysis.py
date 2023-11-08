'''
functions for analysis of generated lightcurves
'''

import json
import numpy as np
import os
import pandas as pd
import subprocess
import time

from argparse import Namespace

from functools import wraps

from nmma.em import analysis

from utils.misc import strtime, suppress_print


def lightcurve_analysis(lightcurve_path, model, prior, outdir, label, tmax=None, slurm=False, **kwargs):
    '''
    Uses nmma to analyse a given lightcurve against a specific model and prior
    
    Args:
    - lightcurve_path (str): path to lightcurve file
    - model (str): model to use (must exist in nmma)
    - prior (str): path to prior file (must match model)
    - outdir (str): path to output directory (will be created if it doesn't exist)
    - label (str): label for analysis files
    - tmax (float): maximum time to consider in analysis (default=None, which means use all data)
    - slurm (str): whether to submit via slurm (default=False). If a string, will use create_slurm_job and submit_slurm_job to create and submit a job file. currrently only accepts msi or expanse as cluster options
    
    Returns:
    - results_path (str): path to results file
    - bestfit_path (str): path to bestfit file
    '''
    dry_run = kwargs.get('dry_run', False)
    assert os.path.exists(lightcurve_path), 'lightcurve file {} does not exist'.format(lightcurve_path)
    os.makedirs(outdir, exist_ok=True)
    env = kwargs.get('env', 'nmma_env')
    
    if not tmax:
        try:
            lightcurve_df = pd.read_json(lightcurve_path)
            # print('lightcurve_df ',lightcurve_df)
            tmax = lightcurve_df.max()[0][0]+0.1 - lightcurve_df.min()[0][0] ## should return the last time in the lightcurve
        except:
            tmax = 21 ## nmma might not like this 
    # print('tmax is {}'.format(tmax))
    trigger_time = get_trigger_time(lightcurve_path)
    
    
    args = Namespace(
        data=lightcurve_path,
        injection=None,
        model=model,
        prior=prior,
        label=label,
        trigger_time=trigger_time, ## may tweak this
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
        filters="ztfg,ztfr,ztfi",
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
        plot=False,
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
    def analysis_main(args):
        analysis.main(args)
        
    if slurm:
        current_time = strtime()
        print(f'[{current_time}] running {label} via slurm')
        job_path = create_slurm_job(lightcurve_path, model, label, prior, outdir, tmax, cluster=str(slurm), rootdir='/expanse/lustre/projects/umn131/tbarna/', **kwargs)
        # print(f'created job file {job_path}')
        submit_slurm_job(job_path, **kwargs) if not dry_run else print('dry run, not submitting job')
        time.sleep(0.1)
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
    
    if tmax_array is None:
        try:
            lightcurve_df = pd.read_json(lightcurve_path)
            tmax = lightcurve_df.max()[0][0] - lightcurve_df.min()[0][0] ## should return the last time in the lightcurve
            tmax_array = np.arange(3.1,tmax+0.1,2)
        except:
            tmax_array = np.arange(3.1,20.1,2) ## nmma might not like this 
    
    results_paths = []
    bestfit_paths = []
    for tmax in tmax_array:
        tmax_label = fit_label + '_tmax_' + str(int(tmax)).zfill(2) ## imposes a label of the format 'lc_{true_model}_{idx}_fit_{model}_tmax_{tmax}'
        if os.path.exists(os.path.join(model_outdir, tmax_label + '_result.json')):
            print(f'{tmax_label} has already been fit, skipping')
            continue
        else:
            try:
                results_path, bestfit_path = lightcurve_analysis(lightcurve_path, model, prior, model_outdir, label=tmax_label, tmax=tmax, threading=threading, **kwargs)
                results_paths.append(results_path)
                bestfit_paths.append(bestfit_path)
            except Exception as e:
                ## print what the error is
                print('exception: ',e)
                print(f'analysis of {tmax_label} failed, skipping')
                continue
    return results_paths, bestfit_paths

def check_completion(result_paths, t0, t0_submission, timeout=71.9):
    '''
    checks for truthiness of all json files existing in output directory
    
    args:
    - result_paths (list): list of the expected lightcurve result paths (including relative path)
    - t0 (time object): time of trigger (assign time.time() at start of analysis)
    - t0_submission (time object): time following submission of all analyses, used for calculating timeout
    - timeout (float): time in hours to wait until returning False even with incomplete analysis
    
    returns:
    - completion_status (bool): whether all lightcurves have been analysed
    - completed_analyses (array): array of lightcurve labels that have been analysed
    '''
    
    total_analyses = len(result_paths)
    analysis_status = np.array([os.path.exists(result_file) for result_file in result_paths], dtype=bool)
    completed_analyses = np.array(result_paths)[analysis_status]
    completed_analyses_count = np.sum(analysis_status)
    completion_status = completed_analyses_count == total_analyses
    
    current_time = strtime()
    t1 = time.time()
    hours_elapsed = round((t1 - t0) / 3600, 2)
    timeout_elapsed = round((t1 - t0_submission) / 3600, 2) > timeout
    estimated_remaining_time = round((hours_elapsed / completed_analyses_count) * (total_analyses - completed_analyses_count),2) if completed_analyses_count > 0 else 0
    
    if timeout_elapsed:
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
    
    
def create_slurm_job(lightcurve_path, model, label, prior, outdir, tmax, svdpath='~/dsmma_kn_23/svdmodels', rootdir='~/dsmma_kn_23', envpath='/home/cough052/barna314/anaconda3/bin/activate', env='nmma_env',cluster='msi', **kwargs):
    '''
    creates a job file for the MSI cluster (somewhat msi specific, but can adapt for other slurm systems)
    
    Args:
    - lightcurve_path (str): path to lightcurve file
    - model (str): model to use (must exist in nmma)
    - label (str): label for analysis files
    - prior (str): path to prior file (must match model)
    - outdir (str): path to output directory (will be created if it doesn't exist)
    - tmax (float): maximum time to consider in analysis
    - svdpath (str): path to svd models (default='~/dsmma_kn_23/svdmodels')
    - rootdir (str): root path to use for analysis (default='~/dsmma_kn_23')
    - envpath (str): path to anaconda installation (default='/home/cough052/barna314/anaconda3/bin/activate')
    - env (str): name of environment to use (default='nmma_env')
    - cluster (str): name of cluster to use (default='msi'). Also accepts expanse
    
    Returns:
    - job_path (str): path to job file
    '''

    os.makedirs(outdir, exist_ok=True)
    outfile = os.path.join(outdir, f'%x_%j.out')
    errfile = os.path.join(outdir, f'%x_%j.err')
    job_path = os.path.join(outdir, label + '.sh')
    trigger_time = get_trigger_time(lightcurve_path)
    dry_run = kwargs.get('dry_run', False)
    filters = ','.join(kwargs.get('filters', ['ztfg'])) ## assumes filters is a list
    if dry_run and os.path.exists(job_path):
        print(f'{job_path} already exists (dry run)')
        # return job_path
    ## workaround for path length limit in fortran
    outdir_string_length = len(outdir)
    if outdir_string_length > 64: 
        # print(f'Warning: outdir ({outdir}) string length is {outdir_string_length}, which exceeds the 64 character limit for fortran')
        relative_outdir = os.path.join(rootdir,outdir)
        outdir = './'
        lightcurve_path = os.path.join(rootdir, lightcurve_path)
        prior = os.path.join(rootdir, prior)
    # if not os.path.exists(lightcurve_path):
    #     lightcurve_path = os.path.join('~/dsmma_kn_23', lightcurve_path)
    #     if not os.path.exists(lightcurve_path):
    #         raise ValueError(f'lightcurve_path {lightcurve_path} does not exist')
    lightcurve_path = os.path.abspath(lightcurve_path)
    tmin = kwargs.get('nmma_tmin',0.1)
        
    
    cmd_str = [ 'lightcurve-analysis',
                '--data', lightcurve_path,
                '--model', model,
                '--label', label,
                '--prior', prior,
                '--svd-path', svdpath,
                '--filters', filters,
                '--tmin', str(tmin),
                '--tmax', str(tmax),
                '--dt', '0.5',
                '--trigger-time', str(trigger_time),
                '--error-budget', '1',
                '--nlive', '1024',
                '--ztf-uncertainties',
                # '--ztf-sampling',
                '--ztf-ToO', '180',
                '--outdir', outdir, 
                '--bestfit',
                " --detection-limit \"{\'r\':21.5, \'g\':21.5, \'i\':21.5}\"",
                "--remove-nondetections",
                # "--verbose",
                #'--plot'
            ]
    if kwargs.get('nmma_plot', True):
        cmd_str.append('--plot')
    
    ## create job file
    with open(job_path, 'w') as f:
        f.write('#!/bin/bash\n')
        if cluster == 'expanse':
            f.write('#SBATCH --partition=shared\n')
            f.write('#SBATCH --account=umn131\n')
        f.write('#SBATCH --job-name=' + label + '\n')
        f.write('#SBATCH --time=01:59:00\n')
        f.write('#SBATCH --nodes=1\n')
        f.write('#SBATCH --ntasks=1\n')
        f.write('#SBATCH --cpus-per-task=2\n')
        f.write('#SBATCH --mem=8gb\n')
        f.write(f'#SBATCH -o {outfile}\n')
        f.write(f'#SBATCH -e {errfile}\n')
        f.write('#SBATCH --mail-type=ALL\n')
        f.write('#SBATCH --mail-user=ztfrest@gmail.com\n')
        if outdir_string_length > 64: ## should output to './' while inside of the outdir
            f.write(f'cd {relative_outdir}\n')
        else:
            f.write(f'cd {rootdir}\n')
        if cluster == 'msi':
            f.write(f'source {envpath} {env}\n')
        else:
            f.write(f'source activate {env}\n')
        f.write(' '.join(cmd_str))
    
    return job_path

def submit_slurm_job(job_path, delete=False, **kwargs):
    '''
    submits a job to a cluster
    
    Args:
    - job_path (str): path to job file
    - delete (bool): whether to delete the job file after submission (default=False)
    
    Returns:
    - None
    '''
    if kwargs.get('resubmit', False):
        submission_cmd = f'sbatch {job_path}'
        subp = subprocess.run(submission_cmd, shell=True, capture_output=True)
        if delete:
            os.remove(job_path) 
    else:
        current_time = strtime()
        potential_results_path = job_path.split('.')[0] + '_result.json'
        if os.path.exists(potential_results_path):
            print(f'[{current_time}] {potential_results_path} already exists, skipping submission')
        
def get_trigger_time(lightcurve_path):
    '''
    gets trigger time from lightcurve file
    
    Args:
    - lightcurve_path (str): path to lightcurve file
    
    Returns:
    - trigger_time (float): trigger time of lightcurve
    '''
    lightcurve_df = pd.read_json(lightcurve_path)
    lc_keys = list(lightcurve_df.keys())
    trigger_time = lightcurve_df[lc_keys[0]][0][0]
    return trigger_time