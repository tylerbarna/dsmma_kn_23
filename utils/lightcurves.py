'''
creates lightcurves from a given injection file using nmma
'''

import numpy as np
import os 

from argparse import Namespace 

from nmma.em import create_lightcurves

def generate_lightcurve(model, injection_path, outDir=None, lightcurve_label=None, filters=['g'], **kwargs):
    '''
    Generates lightcurve for a given injection file
    
    Args:
    - model (str): model to generate lightcurve for
    - injection_path (str): path to injection file
    - outDir (str): output directory for lightcurve (default=None)
    - lightcurve_label (str): identifying label for lightcurve (default=None)
    - filters (list): list of filters to generate lightcurve for (default=['g'])
    
    Returns:
    - lightcurve_path (str): path to lightcurve file
    '''
    assert os.path.exists(injection_path), 'injection file {} does not exist'.format(injection_path)
    if outDir is None:
        outDir = os.path.dirname(injection_path)
    if lightcurve_label is None:
        ## if injection_path=injections/injection_<model>_<label>.json, then lightcurve_label will be <label>
        lightcurve_label = os.path.basename(injection_path).split('.')[0].split('_')[-1]
    lightcurve_filename = 'lc_'+model+'_'+lightcurve_label
    lightcurve_path = os.path.join(outDir, 'lc_'+model+'_'+lightcurve_label+'.dat')
    
    if 'time_series' in kwargs: ## for modification fo time series
        time_series = kwargs['time_series']
        kwargs.pop('time_series')
    else:
        time_series = np.arange(0.01, 20.0 + 0.5, 0.5)
        
    
    args = Namespace( ## based on Michael's changes to nmma unit test
            injection=injection_path,
            label=lightcurve_filename,
            outdir=outDir,
            extension="json",
            model=model,
            svd_path="svdmodels",
            tmin=time_series[0],
            tmax=time_series[-1],
            dt=time_series[1] - time_series[0],
            svd_mag_ncoeff=10,
            svd_lbol_ncoeff=10,
            filters=','.join(filters),
            grb_resolution=5,
            jet_type=0,
            ztf_sampling=False,
            ztf_uncertainties=True,
            ztf_ToO=None,
            rubin_ToO=False,
            rubin_ToO_type=None,
            photometry_augmentation=False,
            photometry_augmentation_seed=0,
            photometry_augmentation_N_points=10,
            photometry_augmentation_filters=','.join(filters),
            photometry_augmentation_times=None,
            plot=True, ## maybe change this to False?
            joint_light_curve=False,
            with_grb_injection=False,
            absolute=False,
            injection_detection_limit=None,
            generation_seed=42,
            interpolation_type="sklearn_gp",
        )
    create_lightcurves.main(args)
    assert os.path.exists(lightcurve_path), 'lightcurve file {} was not created'.format(lightcurve_path)
    
    return lightcurve_path

