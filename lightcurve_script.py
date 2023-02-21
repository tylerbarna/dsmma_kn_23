import subprocess
import sys
import os
import argparse
import glob
from pathlib import Path

import numpy as np
#import pandas as pd
#import matplotlib
#import matplotlib.pyplot as plt
#from matplotlib.pyplot import cm
#from astropy.time import Time

## want to generate 1 kilonova, one afterfglow, and seven supernovae
#subprocess.run('conda activate nmma', shell=True)

models = ['Bu2019lm','TrPi2018', 'nugent-hyper']

def injection_gen(model,inj_label='injection'):
    n_inj = str(1)
    prior_path = os.path.join('../','nmma/priors',model+'.prior')
    cmd_str = ['nmma_create_injection', 
                '--prior-file', prior_path,
                '--eos-file ../nmma/example_files/eos/ALF2.dat', '--binary-type BNS',
                '--n-injection', n_inj,
                '--original-parameters',
                '--extension json'
                ]
    command = ' '.join(cmd_str)
    subprocess.run(command, shell=True)
    
    ## move injection file to injection folder (nmma defaults to cwd)
    inj_path = os.path.join('./injections',model+'_'+inj_label+'.json')
    Path('injection.json').rename(inj_path)
    
    return inj_path

def lc_gen(model, inj_path, out_path,inj_label='injection',filters='g'):
    ## retreive prior
    prior_path = os.path.join('../','nmma/priors',model+'.prior')
    outfile = os.path.join(out_path, model+'_lc_'+inj_label+'.csv')
    cmd_str = ['light_curve_analysis',
                    '--model', model,
                    '--label', inj_label,
                    '--prior', prior_path,
                    '--injection', inj_path,
                    '--injection-num', '0',
                    '--generation-seed', '42',
                    '--filters', filters,
                    '--tmin', '0.1',
                    '--tmax', '20',
                    '--dt', '0.5',
                    '--error-budget', '1',
                    '--nlive', '512',
                    '--remove-nondetections',
                    '--ztf-uncertainties',
                    '--ztf-sampling',
                    '--ztf-ToO', '180',
                    '--outdir', out_path,
                    '--injection-outfile', outfile
                    ]
    command = ' '.join(cmd_str)
    subprocess.run(command, shell=True)
    
for model in models:
    if model == 'nugent-hyper':
        lc_count = 7
    else:
        lc_count = 0
    
    for item in range(lc_count):
        inj_path = injection_gen(model,inj_label='injection_'+str(item))
        lc_gen(model=model, inj_path=inj_path, out_path='./injections',inj_label='injection_'+str(item),filters='g')


## use create lightcurve from injection

## make sure tmin and tmax does the right thing

## check on thursday by five if haven't gotten data to Ana by then