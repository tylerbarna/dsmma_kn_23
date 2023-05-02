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
    
# results = glob.glob('./fits/*/*result.json')
# print("Found {} results".format(len(results)))

# root_directory = Path('./fits/')
# total_size = sum(f.stat().st_size for f in root_directory.glob('**/*') if f.is_file()) / 1024**3
# print("Total size: {:.2f} GB".format(total_size))
# json_size = sum(f.stat().st_size for f in root_directory.glob('**/*result.json') if f.is_file()) / 1024**3
# print("JSON size: {:.2f} GB".format(json_size))
# print('json files occupy {:.2f}% of the total size'.format(json_size / total_size * 100))

# start = time.time()
# jsons = [read_json(f) for f in results]
# stop = time.time()
# print("Reading {} json files took {:.2f} seconds \n(average {:.2f} sec/file)".format(len(jsons), stop - start, (stop - start) / len(jsons)))

# posterior_samples = [j['posterior'] for j in jsons]

def get_lc(file, tmax=False,remove_nondetections=False):
    '''imports dat file as a pandas dataframe'''
    df = pd.read_csv(file, sep=' ', header=None, names=['t', 'filter', 'mag', 'mag_unc'])
    
    df['t'] = Time(pd.to_datetime(df['t'])).mjd ## convert to mjd
    df['t'] = df['t'] - df['t'].min() +1e-2 ## set t=0 to first observation
    if tmax:
        df = df[df['t'] < tmax]
    if remove_nondetections:
        df = df[df['mag_unc'] != np.inf]
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
    '''Calculate residuals between a light curve and data'''
    # assert len(lc) == len(data):
    resids = 0
    for filter in data['filter'].unique():
        t_sample = data[data['filter'] == filter]['t']
        lc_filt = lc[filter] #gen_lc(json_path, modelDict(t_sample)['Bu2019lm'], t_sample)[1]
        data_filt = data[(data['filter'] == filter) & (data['mag_unc'] != np.inf)]
        resids += np.sum(np.abs(lc_filt - data_filt['mag']))/ data_filt['mag_unc']/len(lc_filt) ## updated in .py script
    return resids

def create_series(json, residuals=False):
    '''creates a pandas series from a bilby json file (already read in)'''
    label_dict = get_labels(json)
    bp_dict, likelihood_dict = get_best_params(json)
    obj_dict = {**label_dict,  **likelihood_dict, **bp_dict,}
    obj_series = pd.Series(obj_dict)
    
    if residuals:
        # print(bp_dict)
        tmax = label_dict['tmax']
        data = get_lc('./injection_sample/lc_{}.dat'.format(label_dict['candidate']),
                      tmax=tmax, remove_nondetections=True) ## should be a function argument
        ## need residuals to be calculated for only the detections
        t_sample = np.array(data['t'])
        # print(type(t_sample))
        model = modelDict(t_sample)[label_dict['model']]
        # print("json file: {}".format(json['label']))
        # print("model: {}".format(model))
        # if model == GRBLightCurveModel(model='TrPi2018', sample_times=t_sample):
        #     print(json['log10_E0'])
        
        bf_lc, _ = gen_lc(json, model, t_sample)
        resids = calc_resids(bf_lc, data)
        obj_series['residuals'] = resids
    return obj_series

def create_df(jsons, residuals=False):
    '''creates a pandas dataframe from a list of bilby json files (already read in)'''
    return pd.DataFrame([create_series(j, residuals) for j in jsons]).sort_values(by=['candidate','model','tmax']).reset_index(drop=True)



def plot_lc(json_path, remove_nondetections=True, verbose=False, ax=None, lines=False, **kwargs):
    bf_json = read_json(json_path)
    labels = get_labels(bf_json)
    model = labels['model']
    print(labels) if verbose else None
    dataPath = './injection_sample/lc_{}.dat'.format(labels['candidate'])
    lc_data = get_lc(dataPath, tmax=labels['tmax'], remove_nondetections=remove_nondetections)
    sample_times = lc_data['t'].copy().to_numpy()
    if 'added_time' in kwargs.keys():
        sample_times = np.append(sample_times, kwargs['added_time'])
        sample_times.sort()
        print(sample_times)
        kwargs.pop('added_time')
    elif 'offset' in kwargs.keys():
        sample_times[0] += kwargs['offset']
        kwargs.pop('offset')
    elif sample_times[0] == 0:
        sample_times[0] += 0.1
    
    
    lc_fit, lc_fit_labels = gen_lc(bf_json, modelDict(sample_times)[model], sample_times)
    print(modelDict(lc_data['t'])[model]) if verbose else None
    # if sample_times[0] == 1:
    #     sample_times -= 1
    
    bp_dict = get_best_params(bf_json)
    print(bp_dict) if verbose else None
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(8, 8), facecolor='w', edgecolor='k')
    #lc_data = lc_data[lc_data['filter'].isin]
    detections = lc_data[lc_data['mag_unc'] != np.inf]
    detections.plot(x='t', y='mag', yerr='mag_unc', ax=ax, marker='o', linestyle='-',c='g', edgecolor='k', label='data', s=50, zorder=100, kind='scatter')
    ax.plot(detections['t'], detections['mag'], linestyle='-',c='g', alpha=0.5, lw=2, zorder=99)
    #lc_data[lc_data['mag_unc'] != np.inf].plot(x='t', y='mag', yerr='mag_unc', ax=ax, marker='o', c='g', lw=2, zorder=99, alpha=0.5, legend=False)
    if not remove_nondetections:
        lc_data[lc_data['mag_unc'] == np.inf].plot(x='t', y='mag', ax=ax, marker='v',c='g', linestyle='-',edgecolor='k', s=50, zorder=100, kind='scatter')
    
    fit_label = r'{} ($t_{{max}}$={:.0f})'.format(model, labels['tmax'])
    ax.scatter(sample_times, lc_fit['g'], label=fit_label,zorder=2, **kwargs)
    ax.plot(sample_times, lc_fit['g'],zorder=1, **kwargs) if lines else None
    ax.title.set_text("object: {}".format(labels['candidate']))
    ax.set_xlim(-0.2, )
    
    ax.legend()
    ax.invert_yaxis()
    ax.set_ylim(22,)
    ax.grid()
    return lc_data, lc_fit

df = pd.read_csv('fit_results_residuals.csv')
fig, ax = plt.subplots(1, 1, figsize=(8, 8), facecolor='w', edgecolor='k')
marker_iter = ['.','v', 'o']
added_times = np.linspace(1e-3, 2, 100)
filePath = 'fits/nugent-hyper_3_fit_nugent-hyper/nugent-hyper_3_fit_nugent-hyper_t_15_result.json'
# filePath = 'fits/TrPi2018_0_fit_TrPi2018/TrPi2018_0_fit_TrPi2018_t_15_result.json'
#filePath = 'fits/Bu2019lm_0_fit_Bu2019lm/Bu2019lm_0_fit_Bu2019lm_t_15_result.json'
#filePath = 'fits/Bu2019lm_0_fit_nugent-hyper/Bu2019lm_0_fit_nugent-hyper_t_15_result.json'
data, fit = plot_lc(filePath, remove_nondetections=True, verbose=False, ax=ax, lines=True, c='k', added_time=added_times)
ax.axvline(0.5, c='r', ls='--')
plt.show();
