'''
functions for analysis of generated lightcurves
'''

import numpy as np
import os
import pandas as pd

from argparse import Namespace

from nmma.em import analysis


def lightcurve_analysis(lightcurve_path, model, prior, outdir, label, tmax=None):
    '''
    Uses nmma to analyse a given lightcurve against a specific model and prior
    
    Args:
    - lightcurve_path (str): path to lightcurve file
    - model (str): model to use (must exist in nmma)
    - prior (str): path to prior file (must match model)
    - outdir (str): path to output directory (will be created if it doesn't exist)
    - label (str): label for analysis files
    - tmax (float): maximum time to consider in analysis (default=None, which means use all data)
    
    Returns:
    - results_path (str): path to results file
    - bestfit_path (str): path to bestfit file
    '''
    assert os.path.exists(lightcurve_path), 'lightcurve file {} does not exist'.format(lightcurve_path)
    
    if not tmax:
        try:
            lightcurve_df = pd.read_json(lightcurve_path)
            tmax = lightcurve_df.max()[0][0] ## should return the last time in the lightcurve
        except:
            tmax = np.inf ## nmma might not like this 
    
    args = Namespace(
        data=lightcurve_path,
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
        verbose=False,
    ) 
    
    analysis.main(args)
    
    results_path = os.path.join(outdir, label + "_result.json")
    bestfit_path = os.path.join(outdir, label + "_bestfit.json")
    return results_path, bestfit_path