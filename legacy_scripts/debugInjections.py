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

from nmma.em.model import SimpleKilonovaLightCurveModel, GRBLightCurveModel, SVDLightCurveModel, KilonovaGRBLightCurveModel, GenericCombineLightCurveModel, SupernovaLightCurveModel, ShockCoolingLightCurveModel

from nmma.em.injection import create_light_curve_data as cld

snModel = lambda t: SupernovaLightCurveModel(sample_times=t, model='nugent-hyper')
grbModel = lambda t: GRBLightCurveModel(sample_times=t, model='TrPi2018')
knModel = lambda t: SVDLightCurveModel(sample_times=t, model='Bu2019lm')

modelDict = lambda t: {'nugent-hyper':snModel(t), 'TrPi2018':grbModel(t), 'Bu2019lm':knModel(t)}

directory = './injections-augmented'

def read_injection(path_to_file):
    with open(path_to_file) as p:
        return json.load(p)

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

def get_lc(file, tmax=False,remove_nondetections=False):
    '''imports dat file as a pandas dataframe'''
    df = pd.read_csv(file, sep=' ', header=None, names=['t', 'filter', 'mag', 'mag_unc'])
    
    df['t'] = Time(pd.to_datetime(df['t'])).mjd ## convert to mjd
    df['t'] = df['t'] - df['t'].min() +1e-3 ## set t=0 to first observation
    if tmax:
        df = df[df['t'] < tmax]
    if remove_nondetections:
        df = df[df['mag_unc'] != np.inf]
    return df

model = 'nugent-hyper'
lightcurve = get_lc('./injections-augmented/lc_'+model+'_00000.dat')
print(lightcurve)
injection = read_injection('./injections-augmented/injection_'+model+'_00000.json')['injections']['content']
injection = {k:i[0] for k, i in injection.items()}
print(injection)

lightcurve_times = lightcurve['t'].values
print(lightcurve_times)

model = modelDict(lightcurve_times)[model]
print(model)
injected_lightcurve = model.generate_lightcurve(lightcurve_times, parameters=injection)[1]['g']
injected_lightcurve = luminosity(injection['luminosity_distance'], injected_lightcurve)
print(injected_lightcurve)

fig, ax = plt.subplots()
plt.plot(lightcurve_times, injected_lightcurve, label='injected')
plt.plot(lightcurve_times, lightcurve['mag'], label='observed')
plt.legend()
ax.invert_yaxis()
plt.show()
fig, ax = plt.subplots()
plt.plot(lightcurve_times, (lightcurve['mag'] - injected_lightcurve)/lightcurve['mag']*100, label='disparity in injection vs original (%)')
plt.legend()
# ax.invert_yaxis()
plt.show()