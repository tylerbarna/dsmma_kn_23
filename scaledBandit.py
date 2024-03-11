import argparse
import glob
import numpy as np
import os
import time

import sys

from utils.lightcurves import retime_lightcurve #############################################################
sys.path.append('~/dsmma_kn_23') #############################################################

from concurrent.futures import ProcessPoolExecutor

parser = argparse.ArgumentParser(description='Do analysis on light curves')

parser.add_argument('-m','--models', 
                    type=str, nargs='+', 
                    default=['nugent-hyper','Me2017','TrPi2018'],
                    choices=['nugent-hyper','Bu2019lm','TrPi2018', 'Me2017', 'Piro2021'], 
                    help='models to generate light curves for'
)

parser.add_argument('-tm', '--target-model',
                    type=str,
                    default='Me2017',
                    choices=['nugent-hyper','Bu2019lm','TrPi2018', 'Me2017', 'Piro2021'], 
                    help='model to use as the target for the bandit'
)

parser.add_argument('-stat', '--target-statistic',
                    type=str,
                    default='log_likelihood',
                    choices=['log_likelihood','log_bayes_factor'],
                    help='statistic to use for reward in bandit'
)

parser.add_argument('-r','--reward',
                    type=str,
                    default='ucb',
                    help='which reward strategy to use (default: ucb)'
)

# parser.add_argument('-f','--filters',
#                     type=str,
#                     default='g',
#                     help='filters to generate light curves for (choices for ztf are ztfr,ztfg,ztfi)'
# )

parser.add_argument('-p','--priors',
                    type=str,
                    default='/home/tbarna/dsmma_kn_23/priors',
                    help='path to the prior files'
)

# parser.add_argument('--data',
#                     type=str,
#                     required=True,
#                     help='path to lightcurves'
# )

parser.add_argument('--tmin',
                    type=float,
                    default=3.1,
                    help='tmin value to use for all light curves (default: 3.1)'
)

parser.add_argument('--tmax',
                    type=float,
                    default=11.1,
                    help='tmax value to use for all light curves (default: 11.1)'
)

parser.add_argument('--tstep',
                    type=float,
                    default=1.0,
                    help='tstep value to use for all light curves (default: 1.0)'
)

parser.add_argument('--min-detections',
                    type=int,
                    default=3,
                    help='minimum number of detections required for a light curve to be considered valid (default=3)'
)

parser.add_argument('--min-detections-cutoff',
                    type=float,
                    default=3.1,
                    help='time after start of lightcurve to consider points for when validating (default=3.1)'
)

parser.add_argument('--cadence',
                    type=float,
                    default=0.5,
                    help='cadence of light curve (default=0.5)'
)

parser.add_argument('--nsteps',
                    type=int,
                    default=4,
                    help='number of intervals to use for bandit (default: 4)'
)

parser.add_argument('--nsamples',
                    type=int,
                    default=100,
                    help='number of instances to run (default: 100)'
)


parser.add_argument('--outdir',
                    type=str,
                    default='./fits',
                    help='path to output directory'
)

parser.add_argument('--timeout',
                    type=float,
                    default=1,
                    help='timeout in hours (default: 1 hours)'
)

parser.add_argument('--cluster',
                    type=str,
                    default='expanse',
                    help='cluster to run on (default: expanse)',choices=['msi','expanse','']
)

parser.add_argument('--env',
                    type=str,
                    default='nmma_dev',
                    help='conda environment to run on (default: nmma_dev)'
)


args = parser.parse_args()

## generate the lightcurves, with a bunch of subdirectories corresponding to each batch of 9 lightcurves
num_samples = args.nsamples
models = args.models
target_model = args.target_model
target_statistic = args.target_statistic
reward = args.reward
outdir = args.outdir
min_detections = args.min_detections
min_detections_cuttoff = args.min_detections_cutoff
filters = 'ztfg' #[args.filters] if type(args.filters) == str else args.filters



sample_count = np.arange(num_samples) 
sample_idx_offset = sample_count * 10 ## maybe not the most resilient method

sample_outdirs = [os.path.join(outdir, f'{str(idx).zfill(3)}') for idx in sample_idx_offset]
[os.makedirs(outdir, exist_ok=True) for outdir in sample_outdirs]

idx_to_delete = []
for sample_idx, sample_outdir in enumerate(sample_outdirs):
    if os.path.exists(os.path.join(sample_outdir, 'fit_stats.json')):
        print(f'fits already completed for {sample_outdir}. Skipping')
        idx_to_delete.append(sample_idx)
        num_samples -= 1

## delete the sample_outdirs that have already been completed
sample_outdirs = [sample_outdirs[i] for i in range(len(sample_outdirs)) if i not in idx_to_delete]
sample_idx_offset = [sample_idx_offset[i] for i in range(len(sample_idx_offset)) if i not in idx_to_delete]

print(f'Generating lightcurves for {num_samples} samples')
for idx_offset, sample_outdir in zip(sample_idx_offset, sample_outdirs):
    gen_command_array = [
        'python3',
        'generation_script.py',
        '--models', ' '.join(models),
        '--outdir', sample_outdir,
        '--min-detections', str(min_detections),
        '--min-detections-cutoff', str(min_detections_cuttoff),
        '--cadence', str(args.cadence),
        '--index-offset', str(idx_offset)
    ]
    gen_command = ' '.join(gen_command_array)
    
    os.system(gen_command)


## adjust the lightcurves
lightcurve_paths = sorted(glob.glob(os.path.join(args.outdir,'**','lc*.json')))

# with ProcessPoolExecutor() as executor:
#     for lc in lightcurve_paths:
#         executor.submit(retime_lightcurve, lc)
#     # [executor.submit(retime_lightcurve, lc) for lc in lightcurve_paths]
with ProcessPoolExecutor() as executor:
    for lc in executor.map(retime_lightcurve, lightcurve_paths):
        pass


## run the bandit
bandit_command_list = []
for sample_outdir in sample_outdirs:
    bandit_command_array = [
        'python3',
        'simple_bandit/RunBandit.py',
        '--models', ' '.join(models),
        '--target-model', target_model,
        '--target-statistic', target_statistic,
        '--reward', reward,
        '--priors', args.priors,
        '--data', sample_outdir,
        '--outdir', sample_outdir,
        '--nsteps', str(args.nsteps),
        '--timeout', str(args.timeout),
        '--cluster', args.cluster,
        '--env', args.env,
        '--clean-run'
    ]
    bandit_command = ' '.join(bandit_command_array)
    bandit_command_list.append(bandit_command)

def run_bandit(bandit_command):
    os.system(bandit_command)
    
with ProcessPoolExecutor() as executor:
    for _ in executor.map(run_bandit, bandit_command_list):
        pass