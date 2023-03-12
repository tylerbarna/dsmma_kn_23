import subprocess
import sys
import os
import argparse
import glob
from pathlib import Path
import json
import time

import numpy as np
import pandas as pd

from astropy.time import Time
#import matplotlib
#import matplotlib.pyplot as plt
#from matplotlib.pyplot import cm
#from astropy.time import Time

## want to generate 1 kilonova, one afterfglow, and seven supernovae
#subprocess.run('conda activate nmma', shell=True)
parser = argparse.ArgumentParser(description='Generate light curves for a given model')

parser.add_argument('-m','--models', type=str, nargs='+', default=['nugent-hyper','Bu2019lm','TrPi2018'], help='models to generate light curves for')

args = parser.parse_args()
models = args.models

if not os.path.exists('./injections'):
    os.mkdir('./injections')

#models = ['TrPi2018']#['nugent-hyper','Bu2019lm','TrPi2018'] #
#priors = [ os.path.join('/home/cough052/shared/NMMA/priors/',model) for model in models]
priors = [os.path.join('./priors/',model+'.prior') for model in models]

def injection_gen(model,inj_label='injection'):
    n_inj = 1
    #prior_path = os.path.join('../','nmma/priors',model+'.prior')
    prior_path = os.path.join('./priors/',model+'.prior')
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

def convert_lc_json(lc_file):
    '''
    takes the output file of lc_gen and converts the json into a dat file readable by nmma's light_curve_analysis
    '''
    if not os.path.exists(lc_file):
        print('file {} does not exist'.format(lc_file))
        exit()
    with open(lc_file, 'r') as f:
        data = json.load(f)
    df_all = pd.DataFrame()
    for filt, vals in data.items():
        df = pd.DataFrame(vals, columns=['jd', 'mag', 'mag_unc'])
        df['filter'] = filt
        df['isot'] = Time(df['jd']+2400000.5, format='jd').isot
        df['limmag'] = [mag if unc == np.inf else 99 for mag, unc in zip(df['mag'], df['mag_unc'])]
        df_all = pd.concat([df_all, df],ignore_index=True)
    df_all[['isot','filter','mag','mag_unc']].to_csv(lc_file.replace('.json','.dat'), sep=' ', index=False, header=False)

def lc_gen(model, inj_path, out_path,inj_label='injection',filters='r,g,i'):
    ## retreive prior
    #prior_path = os.path.join('../','nmma/priors',model+'.prior')
    prior_path = os.path.join('./priors/',model+'.prior')
    outfile = os.path.join(out_path,'lc_'+model+'_'+inj_label+'.json')
    label = 'lc_'+model+'_'+inj_label
    cmd_str = ['light_curve_generation',
               '--injection', inj_path,
               '--label', label,
               '--model', model,
               '--svd-path', '../nmma/svdmodels',
               '--tmin', '0.1',
               '--tmax', '20',
               '--dt', '0.5',
               '--ztf-uncertainties',
               '--ztf-sampling',
               '--ztf-ToO', '180',
               '--filters', filters,
               '--outdir', out_path,
               ]
    
    #if model == 'nugent-hyper':
    # cmd_str.append('--filters')
    # cmd_str.append(filters)
    command = ' '.join(cmd_str)
    print("lcg command: {}".format(command))
    subprocess.run(command, shell=True)

    # cmd_str = ['light_curve_analysis',
    #             '--model', model,
    #             '--label', inj_label,
    #             '--prior', prior_path,
    #             '--injection', inj_path,
    #             '--injection-num', '0',
    #             '--generation-seed', '42',
    #             '--filters', filters,
    #             '--tmin', '0.1',
    #             '--tmax', '10',
    #             '--dt', '0.5',
    #             # '--ztf-uncertainties',
    #             # '--ztf-sampling',
    #             # '--ztf-ToO', '180',
    #             '--outdir', out_path,
    #             '--svd-path', models_path,
    #             '--injection-outfile', outfile
    #           ]
    # command = ' '.join(cmd_str)
    # subprocess.run(command, shell=True)
    
    ## rename output file of light_curve_analysis (temporary hack)
    dat_files = glob.glob(os.path.join(out_path,'*.dat'))
    recent_file = max(dat_files, key=os.path.getctime)
    if recent_file == outfile:
        return outfile
    else:
        Path(recent_file).rename(outfile)
    
    ## convert json to dat file
    convert_lc_json(outfile)
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
    
inj_gen_time_dict = {model:[] for model in models}
lc_gen_time_dict = {model:[] for model in models}
for model, prior in zip(models,priors):
    print('starting model: ',model,' with prior: ',prior,'')
    print()
    if model == 'nugent-hyper':
        lc_count = 7
    else:
        lc_count = 1
    
    for item in range(lc_count):
        print('starting injection: ',item,'')
        t0 = time.time()
        inj_path = injection_gen(model,inj_label=str(item))
        #inj_path = './injections/'+model+'_injection_'+str(item)+'.json'
        inj_time = time.time() - t0
        inj_gen_time_dict[model] = np.append(inj_gen_time_dict[model], inj_time)
        print('created injection file: {} ({:.2f} seconds)'.format(inj_path,inj_time))
        
        lc_path = lc_gen(model=model, inj_path=inj_path, out_path='./injections/',inj_label=str(item),filters='g')
        lc_time = time.time() - inj_time - t0
        lc_gen_time_dict[model] = np.append(lc_gen_time_dict[model], lc_time)
        print('created lightcurve file: {} ({:.2f} seconds)'.format(lc_path, lc_time))
        #print()
        lc_dat = lc_path.replace('.json','.dat')
        print('converted lightcurve dat: {}'.format(lc_dat))
        
        #lc_analysis_msi(model=model, lc_path=lc_dat, #inj_label='injection_'+str(item),filters='g') ## may need to correct lc_path
        #print('submitted to msi: ',inj_path)
        ## removing logs since they aren't actually logging anything as of now
        log_files = glob.glob(os.path.join('./injections/','*.log'))
        os.remove(log_files[0])
        #exit()
    print('finished model: ',model,' with prior: ',prior,'')
    print('total injection time: {:.2f} seconds ({:.2f} average)'.format(np.sum(inj_gen_time_dict[model]), np.mean(inj_gen_time_dict[model])))
    print('total lightcurve time: {:.2f} seconds ({:.2f} average)'.format(np.sum(lc_gen_time_dict[model]), np.mean(lc_gen_time_dict[model])))
    print()
    print()
print('finished all models')
#print('total execution time: {:.2f} seconds'.format(np.sum(inj_gen_time_dict.values())+np.sum(lc_gen_time_dict.values())))

