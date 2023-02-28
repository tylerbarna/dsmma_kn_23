import subprocess
import sys
import os
import argparse
import glob
from pathlib import Path
import json

import numpy as np
#import pandas as pd
#import matplotlib
#import matplotlib.pyplot as plt
#from matplotlib.pyplot import cm
#from astropy.time import Time

## want to generate 1 kilonova, one afterfglow, and seven supernovae
#subprocess.run('conda activate nmma', shell=True)

models = ['nugent-hyper','Bu2019lm','TrPi2018'] #
priors = [ os.path.join('/home/cough052/shared/NMMA/priors/',model) for model in models]

def injection_gen(model,inj_label='injection'):
    n_inj = 1
    prior_path = os.path.join('../','nmma/priors',model+'.prior')
    cmd_str = ['nmma_create_injection', 
                '--prior-file', prior_path,
                #'--injection-file', '../nmma/example_files/sim_events/injections.dat',
                '--eos-file ../nmma/example_files/eos/ALF2.dat', '--binary-type BNS',
                '--n-injection', str(n_inj),
                '--original-parameters',
                '--extension json'
                ]
    command = ' '.join(cmd_str)
    subprocess.run(command, shell=True)
    
    ## move injection file to injection folder (nmma defaults to cwd)
    inj_path = os.path.join('./injections/injection_'+model+'_'+inj_label+'.json')
    Path('injection.json').rename(inj_path)
    ## add a simulation_id item to the json file (hack until I can establish the cause)
    with open(inj_path, 'r') as f:
        data = json.load(f)
        content = data['injections']['content']
    if 'simulation_id' not in content.keys():
        content['simulation_id'] = [i for i in range(n_inj)]
        with open(inj_path, 'w') as f:
            f.seek(0,0)
            json.dump(data, f, indent=4)
            f.truncate()
    return inj_path

def lc_gen(model, inj_path, out_path,inj_label='injection',filters='r,g,i'):
    ## retreive prior
    prior_path = os.path.join('../','nmma/priors',model+'.prior')
    outfile = os.path.join(out_path,'lc_'+model+'_'+inj_label+'.dat')
    label = 'lc_'+model+'_'+inj_label
    cmd_str = ['light_curve_generation',
               '--injection', inj_path,
               '--label', label,
               '--model', model,
               '--svd-path', '../nmma/svdmodels',
               '--filters', filters,
                '--tmin', '0.1',
                '--tmax', '10',
                '--dt', '0.5',
                # '--ztf-uncertainties',
                # '--ztf-sampling',
                # '--ztf-ToO', '180',
                '--outdir', out_path,
               ]
    # cmd_str = ['light_curve_analysis',
    #                 '--model', model,
    #                 '--label', inj_label,
    #                 '--prior', prior_path,
    #                 '--injection', inj_path,
    #                 '--injection-num', '0',
    #                 '--generation-seed', '42',
    #                 '--filters', filters,
    #                 '--tmin', '0.1',
    #                 '--tmax', '20',
    #                 '--dt', '0.5',
    #                 '--error-budget', '1',
    #                 '--nlive', '512',
    #                 '--remove-nondetections',
    #                 '--ztf-uncertainties',
    #                 '--ztf-sampling',
    #                 '--ztf-ToO', '180',
    #                 '--outdir', out_path,
    #                 '--injection-outfile', outfile
    #                 ]
    command = ' '.join(cmd_str)
    subprocess.run(command, shell=True)
    
    ## rename output file of light_curve_analysis (temporary hack)
    dat_files = glob.glob(os.path.join(out_path,'*.dat'))
    recent_file = max(dat_files, key=os.path.getctime)
    Path(recent_file).rename(outfile)
    return outfile
    

def lc_analysis_msi(model, lc_path, out_path,inj_label='injection',filters='g'):
    ## retreive prior
    #prior_path = os.path.join('../','nmma/priors',model+'.prior')
    #outfile = os.path.join(out_path, model+'_lc_'+inj_label+'.csv')
    cmd_str = ['sbatch msi_analysis.bash',
                    '--datafile', lc_path,
                    '--candname', inj_label,
                    '--model', model,
                    ]
    command = ' '.join(cmd_str)
    subprocess.run(command, shell=True)
    
for model, prior in zip(models,priors):
    if model == 'nugent-hyper':
        lc_count = 7
    else:
        lc_count = 1
    
    for item in range(lc_count):
        inj_path = injection_gen(model,inj_label=str(item))
        #inj_path = './injections/'+model+'_injection_'+str(item)+'.json'
        print('created injection file: ',inj_path)
        lc_path = lc_gen(model=model, inj_path=inj_path, out_path='./injections/',inj_label=str(item),filters='g')
        print('created lightcurve file: ',lc_path)
        print()
        #lc_analysis_msi(model=model, lc_path=lc_path, #inj_label='injection_'+str(item),filters='g') ## may need to correct lc_path
        #print('submitted to msi: ',inj_path)
        ## removing logs since they aren't actually logging anything as of now
        log_files = glob.glob(os.path.join('./injections/','*.log'))
        os.remove(log_files[0])

