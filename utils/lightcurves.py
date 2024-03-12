'''
creates lightcurves from a given injection file using nmma
'''

import json
import numpy as np
import os 
import pandas as pd

from astropy.time import Time

from argparse import Namespace 

from functools import reduce

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
    lightcurve_path = os.path.join(outDir, lightcurve_filename+'.json')
    
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
            svd_path=kwargs.get('svd_path', "./svdmodels"),
            tmin=time_series[0],
            tmax=time_series[-1],
            dt=time_series[1] - time_series[0],
            svd_mag_ncoeff=10,
            svd_lbol_ncoeff=10,
            filters=','.join(filters),
            grb_resolution=5,
            jet_type=0,
            ztf_sampling=kwargs.get('ztf_sampling', False),
            ztf_uncertainties=True,
            ztf_ToO=None,
            rubin_ToO=False,
            rubin_ToO_type=None,
            photometry_augmentation=False,
            photometry_augmentation_seed=0,
            photometry_augmentation_N_points=10,
            photometry_augmentation_filters=','.join(filters),
            photometry_augmentation_times=None,
            photometric_error_budget=0,
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
            
def read_lightcurve(lightcurve_json, start_time=0.1, cutoff_time=None):
    '''
    Reads in the lightcurve json and returns a pandas dataframe of the lightcurve with associated times, relative to the start time
    
    Args:
    - lightcurve_json (str): path to lightcurve json file
    - start_time (float): relative start time of lightcurve (default=0.1) 
    - cutoff_time (float): cutoff time of lightcurve relative to the start time (default=None). This will remove any data points after that time.
    
    
    Returns:
    - lightcurve_df (pd.DataFrame): dataframe of lightcurve with associated times
    '''
    lightcurve_df_raw = pd.read_json(lightcurve_json) ## this will be in a somewhat messy format
    filters = lightcurve_df_raw.keys() ## get filters
    
    filter_dfs = [] ## initialize empty list of dataframes. Each corresponds to a filter
    for filter in filters:
        filt_df = pd.DataFrame(lightcurve_df_raw[filter].tolist(), columns=['sample_times', filter, f'{filter}_err']) ## convert each filter to a dataframe
        filter_dfs.append(filt_df) ## append to list of dataframes
    lightcurve_df = reduce(lambda left,right: pd.merge(left,right,on=['sample_times'], how='outer'), filter_dfs).fillna(np.inf) ## merge dataframes on sample_times, fill NaNs with np.inf
    lightcurve_df['sample_times'] = round(lightcurve_df['sample_times'] - lightcurve_df['sample_times'].min() + start_time, 2) ## subtract start time from sample_times, also rounds to second decimal place for consistency
    if cutoff_time is not None:
        assert cutoff_time > start_time, 'cutoff_time must be greater than start_time'
        lightcurve_df = lightcurve_df[lightcurve_df['sample_times'] <= cutoff_time]
    
    return lightcurve_df

def validate_lightcurve(lightcurve_path, min_detections=3, min_time=3.1, all_bands=False, **kwargs):
    '''
    Validates that the lightcurve actually has a minimum number of usable detections at the start of the lightcurve.

    Args:
    - lightcurve_path (str): path to lightcurve file
    - min_detections (int): minimum number of detections to be considered valid (default=3)
    - min_time (float): time interval from the start of the lightcurve that needs to contain the minimum number of detections (default=3.1)
    - all_bands (bool): whether or not to require detections in all bands (e.g. for a lightcurve observed in two bands, require both bands to meet observing conditions). When false, only one band needs to meet observing conditions (default=False)

    Returns:
    - valid (bool): whether or not the lightcurve is valid 
    '''
    if not os.path.exists(lightcurve_path): ## ensure lightcurve exists
        print('No lightcurve to Validate!')
        return False
    ## Read in the lightcurve
    lightcurve_df = read_lightcurve(lightcurve_path, **kwargs)
    start_time = lightcurve_df['sample_times'].min()
    end_time = start_time + min_time ## end time is the interval from the start time we want to check for detections

    if all_bands: ## check if all bands meet requirements
        all_bands_meet_criteria = True ## default to true, then check if any band does not meet criteria

        for band in lightcurve_df.columns[1:]:
            min_time_interval = lightcurve_df[(lightcurve_df['sample_times'] >= start_time) & (lightcurve_df['sample_times'] <= end_time)]
            print(min_time_interval[band])
            num_detections = min_time_interval[band].apply(lambda val: 1 if val != np.inf and not np.isnan(val) else 0)
            meets_min_detections = num_detections.sum() >= min_detections
            if not meets_min_detections: ## failure condition, don't need to check other bands
                all_bands_meet_criteria = False
                break
        return all_bands_meet_criteria

    else: ## ensure at least one band meets requirements
        for band in lightcurve_df.columns[1:]:
            min_time_interval = lightcurve_df[(lightcurve_df['sample_times'] >= start_time) & (lightcurve_df['sample_times'] <= end_time)]
            num_detections = min_time_interval[band].apply(lambda val: 1 if val != np.inf and not np.isnan(val) else 0)
            meets_min_detections = num_detections.sum() >= min_detections

            if meets_min_detections:
                return True  ## At least one band meets the criteria

        return False  # None of the bands meet the criteria
 
    
# known_bad = 'injections/lc_TrPi2018_00000.json'
# print(validate_lightcurve(known_bad, min_detections=3, min_time=3.1, all_bands=False))
# known_good = 'injections/lc_Me2017_00000.json'
# print(validate_lightcurve(known_good, min_detections=3, min_time=3.1, all_bands=False))
    
def retime_lightcurve(lightcurve_path, start_time=None, outfile=None):
    '''
    Retimes a lightcurve so it is set to a specific time. By default, will set t=0 to be the first observation, but it can be set to any time.
    
    Args:
    - lightcurve_path (str): path to lightcurve file
    - start_time (float): time to start lightcurve at (default=None). Note that, if it is provided, you will have to make sure it's a value that makes sense for that collection of lightcurves (eg it would be something like 44244). This would be implemented to allow for shifting lightcurves to a specific time.
    - outfile (str): path to output file (default=None). If None, will overwrite the input file.
    
    Returns:
    - outpath (str): path to output file
    '''
    
    with open(lightcurve_path, 'r') as f:
        lc = json.load(f)
    filters = list(lc.keys())
    if start_time is None:
        start_time = np.inf
        for filt in filters:
            times = np.array(lc[filt])[:,0]
            filter_min = np.min(times)
            if filter_min < start_time:
                start_time = filter_min
    for filt in filters:
        lc[filt] = np.array(lc[filt])
        lc[filt][:,0] -= start_time
        lc[filt] = lc[filt].tolist()