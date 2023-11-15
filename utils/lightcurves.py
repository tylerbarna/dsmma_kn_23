'''
creates lightcurves from a given injection file using nmma
'''

import numpy as np
import os 
import pandas as pd
pd.options.mode.chained_assignment = None
import json 

from astropy.time import Time

from argparse import Namespace 

from functools import reduce

from nmma.em import create_lightcurves

from analysis import get_trigger_time

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
            
def read_lightcurve(lightcurve_json, start_time=0.1, cutoff_time=None, **kwargs):
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
    ## Read in the lightcurve
    lightcurve_df = read_lightcurve(lightcurve_path, **kwargs)
    start_time = lightcurve_df['sample_times'].min()
    end_time = start_time + min_time ## end time is the interval from the start time we want to check for detections

    if all_bands: ## check if all bands meet requirements
        all_bands_meet_criteria = True ## default to true, then check if any band does not meet criteria

        for band in lightcurve_df.columns[2:]:
            min_time_interval = lightcurve_df[(lightcurve_df['sample_times'] >= start_time) & (lightcurve_df['sample_times'] <= end_time)]
            num_detections = min_time_interval[band].apply(lambda val: 1 if val != np.inf and not np.isnan(val) else 0)
            meets_min_detections = num_detections.sum() >= min_detections
            if not meets_min_detections: ## failure condition, don't need to check other bands
                all_bands_meet_criteria = False
                break
        return all_bands_meet_criteria

    else: ## ensure at least one band meets requirements
        for band in lightcurve_df.columns[2:]:
            min_time_interval = lightcurve_df[(lightcurve_df['sample_times'] >= start_time) & (lightcurve_df['sample_times'] <= end_time)]
            num_detections = min_time_interval[band].apply(lambda val: 1 if val != np.inf and not np.isnan(val) else 0)
            meets_min_detections = num_detections.sum() >= min_detections

            if meets_min_detections:
                return True  ## At least one band meets the criteria

        return False  # None of the bands meet the criteria
 
def get_filter_df(lightcurve_df, filter):
    '''
    Retreives a dataframe containing only the filter specified. Assumes structure of the read_lightcurve function.
    
    Args:
    - lightcurve_df (pd.DataFrame): dataframe of lightcurve with associated times
    - filter (str): filter to retreive
    
    Returns:
    - filter_df (pd.DataFrame): dataframe of lightcurve with associated times for the specified filter
    '''
    existing_filters = [col for col in lightcurve_df.columns if col not in ['sample_times'] and '_err' not in col]
    assert filter in existing_filters, 'filter {} does not exist in lightcurve'.format(filter)
    filter_df_list = []
    for row in lightcurve_df.iterrows():
        if row[1][filter] != np.inf and row[1][filter] != np.nan:
            filter_df_list.append(row[1])
    filter_df = pd.DataFrame(filter_df_list)
    return filter_df

def generate_lightcurve_dict(lightcurve_df):
    '''
    Generates dictionary in the format needed to dump to a json
    
    Args:
    - lightcurve_df (pd.DataFrame): dataframe of lightcurve with associated times
    
    Returns:
    - lightcurve_dict (dict): dictionary of lightcurve with associated times
    '''
    filters = [col for col in lightcurve_df.columns if col not in ['sample_times'] and '_err' not in col]
    lightcurve_dict = {}
    for filter in filters:
        filter_df = get_filter_df(lightcurve_df, filter)
        sample_times = filter_df['sample_times'].tolist()
        filter_vals = filter_df[filter].tolist()
        filter_errs = filter_df[f'{filter}_err'].tolist()
        ## use sample times to itterate the above 3 lists. if they do not have the same length, then there is an issue
        lightcurve_dict[filter] = [[sample_times[i], filter_vals[i], filter_errs[i]] for i in range(len(sample_times))]
    return lightcurve_dict

def starting_lightcurve(full_lightcurve, outdir, starting_time=2, starting_observations=None, correct_times=False, **kwargs):
        '''
        Retreives a full lightcurve from a lightcurve file and generates a new file with enough observations to start the multi-arm bandit analysis. This is either the first n observations, where n is starting_observations, or the first observations within a certain number of days from the first observation. I would recommend using starting_observations when using ztf sampling and then use starting_time for even/better sampling. If the starting time does not contain at least 2 points, will print a warning and then default to setting starting_observations to 2 even if it's not provided.
        
        Args:
        - full_lightcurve (str): path to full lightcurve file
        - outdir (str): output directory for starting lightcurve file
        - starting_time (float): time interval from the start of the lightcurve that needs to contain the minimum number of detections (default=2)
        - starting_observations (int): number of observations to start with (default=None). You only need to provide the starting_time or starting_observations, but starting_observations will supercede starting_time if both are provided.
        - correct_times (bool): whether or not to correct the times so that the first observation is at the same time as the original lightcurve (default=False)
        
        Returns:
        - starting_lightcurve (str): path to starting lightcurve file
        
        TODO:
        - make it so it checks about non-detections
        - fix the way the correct_times works so it reads in the correct initial time. Right now, it will read in the time of the first detection, so if the lowest time measurement is a non-detection, the times will be thrown off
        '''
        full_lightcurve_df = read_lightcurve(full_lightcurve, start_time = 0, **kwargs)
        filters = [col for col in full_lightcurve_df.columns if col not in ['sample_times'] and '_err' not in col]
        if starting_time and starting_observations is None:
            starting_lightcurve_df = full_lightcurve_df[full_lightcurve_df['sample_times'] <= starting_time]
            if starting_lightcurve_df.shape[0] <= 2:
                print('WARNING: starting lightcurve does not contain at least 2 points. Defaulting to starting_observations=2')
                starting_observations = 2
        if starting_observations is not None:
            ## get the first n observations, where n is starting_observations for each filter
            starting_lightcurve = []
            for filter in filters:
                filter_df = get_filter_df(full_lightcurve_df, filter)
                starting_lightcurve.append(filter_df.iloc[:starting_observations])
            starting_lightcurve_df = pd.concat(starting_lightcurve)
        if correct_times:
            tmin = get_trigger_time(full_lightcurve)
            starting_lightcurve_df.loc[:,'sample_times'] += tmin + 0.1
        ## construct dictionary to write to json. Each key is the filter, and the value for each key is a list of lists, with the sublists containing three terms: sample_times, filter, and filter_err for each observation
        starting_lightcurve_dict = generate_lightcurve_dict(starting_lightcurve_df)
        starting_lightcurve_path = os.path.join(outdir, kwargs.get('lightcurve_label', os.path.basename(full_lightcurve)))
        os.makedirs(outdir, exist_ok=True)
        with open(starting_lightcurve_path, 'w') as f:
            json.dump(starting_lightcurve_dict, f, indent=4)
        return starting_lightcurve_path


def observe_lightcurve(full_lightcurve, previous_lightcurve, outdir, step_size=1,filters=['ztfg'], correct_times=False, **kwargs):
    '''
    Takes in a full lightcurve and a previous lightcurve, and returns a new lightcurve with the next step_size observations. This is useful for simulating observing a lightcurve in real time. 
    
    Args:
    - full_lightcurve (str): path to full lightcurve file
    - previous_lightcurve (str): path to previous lightcurve file
    - outdir (str): output directory for next lightcurve file
    - step_size (int): interval on which to add observations (default=1). For the default, this will add any observations made in the next day.
    - filters (list): list of filters to observe (default=['ztfg']). These filters need to exist
    - correct_times (bool): whether or not to correct the times so that the first observation is at the same time as the original lightcurve (default=False)
    
    Returns:
    - next_lightcurve (str): path to next lightcurve file
    
    TODO:
    - make it so it checks about non-detections
    - make an option so you can specify that you want the next observation regardless of whether or not it's in the next step_size interval (maybe)
    - fix the way the correct_times works so it reads in the correct initial time. Right now, it will read in the time of the first detection, so if the lowest time measurement is a non-detection, the times will be thrown off
    '''
    full_lightcurve_df = read_lightcurve(full_lightcurve, start_time=0, **kwargs)
    previous_lightcurve_df = read_lightcurve(previous_lightcurve, start_time=0, **kwargs)
    start_time = full_lightcurve_df['sample_times'].min()
    end_time = previous_lightcurve_df['sample_times'].max() + step_size ## end time is the interval from the start time we want to check for detections
    new_observations = []
    for filter in filters:
        full_filter_df = get_filter_df(full_lightcurve_df, filter)
        previous_filter_df = get_filter_df(previous_lightcurve_df, filter)
        next_observations = full_filter_df[(full_filter_df['sample_times'] > previous_filter_df['sample_times'].max()) & (full_filter_df['sample_times'] <= end_time)]
        new_observations.append(next_observations)
    new_observations_df = pd.concat(new_observations)
    next_lightcurve_df = pd.concat([previous_lightcurve_df, new_observations_df])
    if correct_times:
            tmin = get_trigger_time(previous_lightcurve)
            next_lightcurve_df.loc[:,'sample_times'] += tmin
    next_lightcurve_dict = generate_lightcurve_dict(next_lightcurve_df)
    next_lightcurve_path = os.path.join(outdir, kwargs.get('lightcurve_label', os.path.basename(full_lightcurve)))
    os.makedirs(outdir, exist_ok=True)
    with open(next_lightcurve_path, 'w') as f:
        json.dump(next_lightcurve_dict, f, indent=4)
    return next_lightcurve_path  