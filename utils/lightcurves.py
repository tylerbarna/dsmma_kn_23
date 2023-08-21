'''
creates lightcurves from a given injection file using nmma
'''

import numpy as np
import os 

from astropy.time import Time

from argparse import Namespace 

from nmma.em import create_lightcurves

def generate_lightcurve(model, injection_path, outDir=None, lightcurve_label=None, filters=['ztfg'], **kwargs):
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
    lightcurve_path = os.path.join(outDir, 'lc_'+model+'_'+lightcurve_label+'.json')
    
    if 'time_series' in kwargs: ## for modification fo time series
        time_series = kwargs['time_series']
        kwargs.pop('time_series')
    else:
        time_series = np.arange(0.01, 20.0 + 0.5, 0.5)
        
    
    args = Namespace( ## based on Michael's changes to nmma unit test
            injection=injection_path,
            label=lightcurve_filename,
            outdir=outDir,
            outfile_type="json", ## new addition
            model=model,
            svd_path="./svdmodels",
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
            photometric_error_budget=None,
            plot=False, ## maybe change this to False?
            joint_light_curve=False,
            with_grb_injection=False,
            absolute=False,
            injection_detection_limit=None,
            generation_seed=42,
            interpolation_type="sklearn_gp",
            increment_seeds=False,
        )
    create_lightcurves.main(args)
    assert os.path.exists(lightcurve_path), 'lightcurve file {} was not created'.format(lightcurve_path)
    
    return lightcurve_path

def lightcurve_conversion(lightcurve_path):
    '''
    Converts lightcurve to be ingestible by light_curve_analysis (this is a temporary solution until the compatibility between light_curve_generation and light_curve_analysis are fixed)
    
    Args:
    - lightcurve_path (str): path to lightcurve file (expected to be a .dat file)
    
    Returns:
    - converted_lightcurve_path (str): path to converted lightcurve file
    '''
    assert os.path.exists(lightcurve_path), 'lightcurve file {} does not exist'.format(lightcurve_path)
    lightcurve_directory = os.path.dirname(lightcurve_path)
    
    with open(lightcurve_path, 'r') as f:
        lines = f.readlines() ## reads in lines
        lines = [line.strip() for line in lines] ## removes newlines

    filters = lines[0].split()[2:] ## skip first 2 items in list ("#", "t[days]"), then get filters
    times = np.array([float(line.split()[0]) for line in lines[1:]]) ## skip first item in list ("#"), then get times
    mags = { filt:[float(line.split()[col]) for line in lines[1:]] for col, filt in enumerate(filters, start=1)} ## dictionary of magnitudes for each filter
    
    isot_times = Time(times+ 40587, format='mjd').isot ## sets times to be in isot format, with 40587 being the MJD of 1970-01-01T00:00:00
    
    converted_lines = []
    for filter in filters:
        filtered_mags = mags[filter]
        for isot_time, mag in zip(isot_times, filtered_mags):
            converted_lines.append('{} {} {}'.format(isot_time, filter, mag))
    
    converted_lightcurve_path = os.path.join(lightcurve_directory, 'converted_'+os.path.basename(lightcurve_path))
    
    with open(converted_lightcurve_path, 'w') as f:
        f.write('\n'.join(converted_lines))
        
    return converted_lightcurve_path 
            

