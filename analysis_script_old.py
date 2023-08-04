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

parser = argparse.ArgumentParser(description='Do analysis on light curves')


parser.add_argument('-m','--models', 
                    type=str, nargs='+', 
                    default=['nugent-hyper','Bu2019lm','TrPi2018'], 
                    help='models to generate light curves for'
)
# parser.add_argument('-f','--filters',
#                     type=str,
#                     default='g',
#                     help='filters to generate light curves for (choices for ztf are r,g,i)'
# )

parser.add_argument('-p','--priors',
                    type=str,
                    default='./priors/',
                    help='path to the prior files'
)

parser.add_argument('--data',
                    type=str,
                    required=True,
                    help='path to data files'
)

parser.add_argument('--outdir',
                    type=str,
                    default='./fits/',
                    help='path to output directory'
)

parser.add_argument('--timeout',
                    type=float,
                    default=71.5,
                    help='timeout in hours (default=72)')


args = parser.parse_args()
models = args.models
outdir = args.outdir
timeout = args.timeout

lc_paths = glob.glob(os.path.join(args.data,'*.dat')) ## list of lightcurve data files
lc_names = [os.path.basename(lc).split('.')[0].replace('lc_','') for lc in lc_paths] ## list of lightcurve names (eg nugent-hyper_0)
print('lightcurve names: {}'.format(lc_names))

def check_completion(lc_names, models, outdir):
        ''''
        check for truthiness of all json files existing in output directory. should find n_models * n_lc_names * 7 json files 
        (format of outdir/{lc_name}_fit_{model}_t_{i}_result.json)
        '''
        expected_json_count = len(lc_names) * len(models) * 7
        json_paths = []
        for lc in lc_names:
                for model in models:
                        json_paths += glob.glob(os.path.join(outdir,'{}_fit_{}*'.format(lc,model),'*_result.json'))
        return len(json_paths) == expected_json_count, len(json_paths) - expected_json_count



## count the number of jobs already submitted to compare against 
existing_jobs_status = subprocess.run('squeue -u barna314', shell=True, capture_output=True)
num_existing_jobs = len(existing_jobs_status.stdout.splitlines())
# print(lc_paths)
# print(lc_names)
#print(lightcurve_names)

for idx, lc in enumerate(lc_names):
    for model in models:

        prior = os.path.join(args.priors,model+'.prior')
        label = '{}_fit_{}'.format(lc,model)
        cmd_str = ['sbatch msi_analysis.sh',
                lc_paths[idx], ## lightcurve data file
                label, ## lightcurve label
                model, ## model name
                prior, ## prior file
                outdir, ## output directory
            
        ]
        command = ' '.join(cmd_str)
        subprocess.run(command, shell=True, capture_output=True)
        print('Submitted job for {}'.format(label))
        print('command: {}'.format(command))

print('Submitted jobs for all lightcurves')

## monitor for completion of all jobs
t0 = time.time()
while True:
        time.sleep(60)
        jobs_completed_bool, remaining = check_completion(lc_names, models, outdir) ## returns true if counts of json files in output directory match expected counts
        t1 = time.time()
        t_hours = (t1 - t0) / 60 / 60
        #current_jobs_status = subprocess.run('squeue -u cough052', shell=True, capture_output=True)
        #num_current_jobs = len(current_jobs_status.stdout.splitlines())
        if t_hours > timeout:
                print('[{}] Jobs taking too long, exiting...'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))
                break
        elif jobs_completed_bool:
                print('[{}] All jobs finished!'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))
                break
        else:
                print('[{}] Waiting for jobs to finish ({} remaining)...'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), remaining))