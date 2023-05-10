import subprocess
import sys
import os
import argparse
from distutils.version import LooseVersion
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

import matplotlib.pyplot as plt
import seaborn as sns

import warnings
warnings.filterwarnings('ignore')
warnings.simplefilter("ignore", UserWarning)

from nmma.em.model import SimpleKilonovaLightCurveModel,GRBLightCurveModel, SVDLightCurveModel, KilonovaGRBLightCurveModel, GenericCombineLightCurveModel, SupernovaLightCurveModel, ShockCoolingLightCurveModel

from nmma.em.injection import create_light_curve_data as cld


parser = argparse.ArgumentParser(description='Generate the dataframes for the light curves')

parser.add_argument('--data',
                    type=str,
                    default='./fits',
                    help='directory containing the results of the fits')

parser.add_argument('--outdir',
                    type=str,
                    default='./',
                    help='output directory for the dataframes')

parser.add_argument('--filename',
                    type=str,
                    default='fit_results',
                    help='filename for the dataframes')

args = parser.parse_args()


snModel = lambda t: SupernovaLightCurveModel(sample_times=t, model='nugent-hyper')
grbModel = lambda t: GRBLightCurveModel(sample_times=t, model='TrPi2018')
knModel = lambda t: SVDLightCurveModel(sample_times=t, model='Bu2019lm')

modelDict = lambda t: {'nugent-hyper':snModel(t), 'TrPi2018':grbModel(t), 'Bu2019lm':knModel(t)}

def luminosity(distance, mag):
    """
    Calculate the luminosity of a source given its distance and apparent magnitude.
    Parameters
    """
    abs = lambda mag, distance: mag + 5 * np.log10(distance * 1e6 / 10.0)
    if type(mag) == np.ndarray:
        return abs(mag, distance)
    elif type(mag) == dict:
        return {k: abs(mag[k], distance) for k in mag.keys()} 

def read_json(path_to_file):
    with open(path_to_file) as p:
        return json.load(p, object_hook=bilby.core.utils.decode_bilby_json)
    
results = glob.glob(os.path.join(args.data,'*/*result.json'))
glob.glob('./fits/*/*result.json')
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

def get_lc(file, tmax=False,remove_nondetections=False):
    '''imports dat file as a pandas dataframe'''
    df = pd.read_csv(file, sep=' ', header=None, names=['t', 'filter', 'mag', 'mag_unc'])
    
    df['t'] = Time(pd.to_datetime(df['t'])).mjd ## convert to mjd
    df['t'] = df['t'] - df['t'].min() ## set t=0 to first observation
    if tmax:
        df = df[df['t'] < tmax]
    df = df[df['mag_unc'] != np.inf] if remove_nondetections else df
    return df

def get_best_params(json_path, verbose=False):
    '''Get the best fit parameters from a bilby json_path file, return as a dictionary'''
    # ll_idx = np.argmin(np.abs(json_path['log_likelihood_evaluations']))
    #best_ll = json_path['log_likelihood_evaluations'][ll_idx]
    post = json_path['posterior']
    ll_idx = np.argmin(np.abs(post['log_likelihood']))
    best_ll = post['log_likelihood'][ll_idx]
    post_keys = list(post.keys())
    print("Best log likelihood evaluation: {}".format(best_ll)) if verbose else None
    log_evidence = json_path['log_evidence']
    log_evidence_err = json_path['log_evidence_err']
    log_bayes_factor = json_path['log_bayes_factor']
    likelihood_dict = dict(zip(['log_likelihood','log_evidence', 'log_evidence_err', 'log_bayes_factor'], [best_ll, log_evidence, log_evidence_err, log_bayes_factor]))
    # print(bp_dict) if verbose else None
    #bp_dict = dict(zip(json_path['search_parameter_keys'], json_path['samples'][ll_idx]))
    # bp_dict = dict(zip(json_path['search_parameter_keys'], json_path['samples'][ll_idx, :]))
    bp_dict = dict(zip(post_keys, [post[k][ll_idx] for k in post_keys]))

    return bp_dict, likelihood_dict

def get_labels(json_path):
    '''get the object label from bilby file, return as a dictionary'''
    raw_label = json_path['label']
    candidate = raw_label.split('_')[0] + '_' + raw_label.split('_')[1]
    model = raw_label.split('_')[3]
    tmax = float(raw_label.split('_')[5])
    keys = ['candidate', 'model', 'tmax']
    label_dict = dict(zip(keys, [candidate, model, tmax]))
    
    return label_dict


def gen_lc(json_path, model, sample_times, verbose=False):
    '''Generate a light curve from a bilby json_path file'''
    bp, like_dict = get_best_params(json_path, verbose=verbose)
    model_type = get_labels(json_path)['model']
    model = modelDict(sample_times)[model_type]
    print(model) if verbose else None
    label = get_labels(json_path)
    print(label) if verbose else None
    print(bp) if verbose else None
    print() if verbose else None
    lc = model.generate_lightcurve(sample_times, parameters=bp)[1]
    lc_abs = luminosity(bp['luminosity_distance'], lc)
    return lc_abs, label

def calc_resids(lc, data):
    '''Calculate residuals between a best fit light curve and actual data'''
    # assert len(lc) == len(data):
    resids = 0
    resids_unc = 0
    chi2 = 0
    for filter in data['filter'].unique():
        t_sample = data[data['filter'] == filter]['t']
        lc_filt = lc[filter] #gen_lc(json, modelDict(t_sample)['Bu2019lm'], t_sample)[1]
        data_filt = data[data['filter'] == filter]
        chi2 += np.sum((lc_filt - data_filt['mag'])**2 / data_filt['mag']) / len(lc_filt) / len(data['filter'].unique())
    return chi2

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
        print("json file: {}".format(json['label']))
        
        t_sample = np.array(data[data['mag_unc'] != np.inf]['t'])
        print("t_sample: {}".format(t_sample))
        if len(t_sample) < 3:
            print("less than 3 detections for this object at t < {}".format(tmax))
            print()
            obj_series['chi2'] = np.inf
            return obj_series
        t_sample[0] += 0.01 ## to prevent a zero value in the light curve
        # print(type(t_sample))]
        model = modelDict(t_sample)[label_dict['model']]
        print("model: {}".format(model))
        # print(model)
        bf_lc, _ = gen_lc(json, model, t_sample)
        print('calculated best fit light curve')
        chi2 = calc_resids(bf_lc, data[data['mag_unc'] != np.inf])
        # print("residual: {:.2f} ({:.2f} with uncertainty)".format(resids, resids_unc))
        print("calculated chi2: {:.4e}".format(chi2))
        
        print()
        # obj_series['residuals'] = resids
        # obj_series['residuals_unc'] = resids_unc
        obj_series['chi2'] = chi2
    return obj_series

def create_df(jsons, residuals=False, verbose=False):
    '''creates a pandas dataframe from a list of bilby json files (already read in)'''
    return pd.DataFrame([create_series(j, residuals, verbose) for j in jsons]).sort_values(by=['candidate','model','tmax']).reset_index(drop=True)

## should add something that defines length or something (maybe encode in filename provided)
t0 = time.time()
df = create_df(jsons, residuals=False)
t1 = time.time()
print("Creating dataframe (no residuals) took {:.2f} seconds".format(t1-t0))
df_name = os.path.join(args.outdir, args.filename+'.csv')
df.to_csv(df_name, index=False)

print('starting to create dataframe with residuals')
t0 = time.time()
df_r = create_df(jsons, residuals=True)
t1 = time.time()
df_r_name = os.path.join(args.outdir, args.filename+'_residuals.csv')
df_r.to_csv(df_r_name, index=False)
