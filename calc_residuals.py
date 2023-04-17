import subprocess
import sys
import os
import argparse
import glob
from pathlib import Path
import json
import time
import bilby
import nmma

import astropy
import numpy as np
import pandas as pd

from astropy.time import Time

from nmma.em.model import SimpleKilonovaLightCurveModel,GRBLightCurveModel, SVDLightCurveModel, KilonovaGRBLightCurveModel, GenericCombineLightCurveModel, SupernovaLightCurveModel, ShockCoolingLightCurveModel

from nmma.em.injection import create_light_curve_data as cld

import warnings
warnings.simplefilter("ignore", UserWarning)

snModel = lambda t: SupernovaLightCurveModel(sample_times=t, model='nugent-hyper')
grbModel = lambda t: GRBLightCurveModel(sample_times=t, model='TrPi2018')
knModel = lambda t: SVDLightCurveModel(sample_times=t, model='Bu2019lm')

modelDict = lambda t: {'nugent-hyper':snModel(t), 'TrPi2018':grbModel(t), 'Bu2019lm':knModel(t)}

def luminosity(distance, mag):
    """
    Calculate the luminosity of a source given its distance and apparent magnitude.
    Parameters
    """
    abs = lambda mag, distance: mag - 5 * np.log10(distance * 1e6 / 10.0)
    if type(mag) == np.ndarray:
        return abs(mag, distance)
    elif type(mag) == dict:
        return {k: abs(mag[k], distance) for k in mag.keys()} 

def read_json(path_to_file):
    with open(path_to_file) as p:
        return json.load(p, object_hook=bilby.core.utils.decode_bilby_json)
    
results = glob.glob('./fits/*/*result.json')
print("Found {} results".format(len(results)))
print()

root_directory = Path('./fits/')
total_size = sum(f.stat().st_size for f in root_directory.glob('**/*') if f.is_file()) / 1024**3
print("Total size: {:.2f} GB".format(total_size))
json_size = sum(f.stat().st_size for f in root_directory.glob('**/*result.json') if f.is_file()) / 1024**3
print("JSON size: {:.2f} GB".format(json_size))
print('json files occupy {:.2f}% of the total size'.format(json_size / total_size * 100))

start = time.time()
jsons = [read_json(f) for f in results]
stop = time.time()
print("Reading {} json files took {:.2f} seconds \n(average {:.2f} sec/file)".format(len(jsons), stop - start, (stop - start) / len(jsons)))

posterior_samples = [j['posterior'] for j in jsons]

# ll_idx = np.argmin(np.abs(jsons[0]['log_likelihood_evaluations']))
# print("Best log likelihood evaluation: {}".format(ll_idx))
# print(jsons[0]['log_likelihood_evaluations'][ll_idx])
# print(jsons[0]['samples'][ll_idx])
# best_params = dict(zip(jsons[0]['search_parameter_keys'], jsons[0]['samples'][ll_idx]))
# print(best_params)

def get_lc(file, tmax=False):
    '''imports dat file as a pandas dataframe'''
    df = pd.read_csv(file, sep=' ', header=None, names=['t', 'filter', 'mag', 'mag_unc'])
    df = df[df['mag_unc'] != np.inf] ## drop non-detections
    df['t'] = Time(pd.to_datetime(df['t'])).mjd ## convert to mjd
    df['t'] = df['t'] - df['t'].min() ## set t=0 to first observation
    if tmax:
        df = df[df['t'] < tmax]
    return df

def get_best_params(json, verbose=False):
    '''Get the best fit parameters from a bilby json file, return as a dictionary'''
    # ll_idx = np.argmin(np.abs(json['log_likelihood_evaluations']))
    #best_ll = json['log_likelihood_evaluations'][ll_idx]
    post = json['posterior']
    ll_idx = np.argmin(np.abs(post['log_likelihood']))
    best_ll = post['log_likelihood'][ll_idx]
    post_keys = list(post.keys())
    print("Best log likelihood evaluation: {}".format(best_ll)) if verbose else None
    log_evidence = json['log_evidence']
    log_evidence_err = json['log_evidence_err']
    log_bayes_factor = json['log_bayes_factor']
    likelihood_dict = dict(zip(['log_likelihood','log_evidence', 'log_evidence_err', 'log_bayes_factor'], [best_ll, log_evidence, log_evidence_err, log_bayes_factor]))
    # print(bp_dict) if verbose else None
    #bp_dict = dict(zip(json['search_parameter_keys'], json['samples'][ll_idx]))
    # bp_dict = dict(zip(json['search_parameter_keys'], json['samples'][ll_idx, :]))
    bp_dict = dict(zip(post_keys, [post[k][ll_idx] for k in post_keys]))

    return bp_dict, likelihood_dict

def get_labels(json):
    '''get the object label from bilby file, return as a dictionary'''
    raw_label = json['label']
    candidate = raw_label.split('_')[0] + '_' + raw_label.split('_')[1]
    model = raw_label.split('_')[3]
    tmax = float(raw_label.split('_')[5])
    keys = ['candidate', 'model', 'tmax']
    label_dict = dict(zip(keys, [candidate, model, tmax]))
    
    return label_dict
    
    return label_dict

def gen_lc(json, model, sample_times, verbose=False):
    '''Generate a light curve from a bilby json file'''
    bp, like_dict = get_best_params(json, verbose=verbose)
    model_type = get_labels(json)['model']
    model = modelDict(sample_times)[model_type]
    print(model) if verbose else None
    label = get_labels(json)
    #print(label) 
    
    # for k, v in bp.items():
    #     if v == 0:
    #         bp[k] = 0.01
    print('parameters: ',bp) 
    print('sample_times: ', sample_times)
    #print()
    lc = model.generate_lightcurve(sample_times, parameters=bp)[1]
    lc_abs = luminosity(bp['luminosity_distance'], lc)
    return lc_abs, label

def calc_resids(lc, data):
    '''Calculate residuals between a light curve and data'''
    # assert len(lc) == len(data):
    resids = 0
    for filter in data['filter'].unique():
        t_sample = data[data['filter'] == filter]['t']
        lc_filt = lc[filter] #gen_lc(json, modelDict(t_sample)['Bu2019lm'], t_sample)[1]
        data_filt = data[data['filter'] == filter]
        resids += np.sum(np.abs(lc_filt - data_filt['mag'])/ data_filt['mag_unc'])
    return resids / len(data['filter'].unique()) / len(data)

def create_series(json, residuals=False, verbose=False):
    '''creates a pandas series from a bilby json file (already read in)'''
    # if verbose:
    #     print('creating series for {} ({} of {})'.format(json['label'], i, len(jsons)))
    label_dict = get_labels(json)
    bp_dict, likelihood_dict = get_best_params(json)
    obj_dict = {**label_dict,  **likelihood_dict, **bp_dict,}
    obj_series = pd.Series(obj_dict)
    
    if residuals:
        # print(bp_dict)
        tmax = label_dict['tmax']
        data = get_lc('./injection_sample/lc_{}.dat'.format(label_dict['candidate']),
                      tmax=tmax) ## should be a function argument
        t_sample = np.array(data['t'])
        t_sample[0] += 0.01 ## to prevent a zero value in the light curve
        # print(type(t_sample))]
        model = modelDict(t_sample)[label_dict['model']]
        print("json file: {}".format(json['label']))
        print("model: {}".format(model))
        # print(model)
        bf_lc, _ = gen_lc(json, model, t_sample)
        resids = calc_resids(bf_lc, data)
        print("residual: {}".format(resids))
        print()
        obj_series['residuals'] = resids
    return obj_series

def create_df(jsons, residuals=False, verbose=False):
    '''creates a pandas dataframe from a list of bilby json files (already read in)'''
    return pd.DataFrame([create_series(j, residuals, verbose) for j in jsons]).sort_values(by=['candidate','model','tmax']).reset_index(drop=True)

t0 = time.time()
df = create_df(jsons, residuals=False)
t1 = time.time()
print("Creating dataframe (no residuals) took {:.2f} seconds".format(t1-t0))
df.to_csv('fit_results.csv', index=False)

t0 = time.time()
df_r = create_df(jsons, residuals=True)
t1 = time.time()
print("Creating dataframe (with residuals) took {:.2f} seconds".format(t1-t0))
df_r.to_csv('fit_results_residuals.csv', index=False)
