import argparse
import glob
import numpy as np
import os
import time

from utils.analysis import timestep_lightcurve_analysis, check_completion
from utils.misc import strtime

parser = argparse.ArgumentParser(description='Do analysis on light curves')


parser.add_argument('-m','--models', 
                    type=str, nargs='+', 
                    default=['nugent-hyper','Bu2019lm','TrPi2018', 'Piro2021'],
                    choices=['nugent-hyper','Bu2019lm','TrPi2018', 'Me2017', 'Piro2021'], 
                    help='models to generate light curves for'
)
# parser.add_argument('-f','--filters',
#                     type=str,
#                     default='g',
#                     help='filters to generate light curves for (choices for ztf are ztfr,ztfg,ztfi)'
# )

parser.add_argument('-p','--priors',
                    type=str,
                    default='~/dsmma_kn_23/priors',
                    help='path to the prior files'
)

parser.add_argument('--data',
                    type=str,
                    required=True,
                    help='path to lightcurves'
)

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

parser.add_argument('--outdir',
                    type=str,
                    default='./fits',
                    help='path to output directory'
)

parser.add_argument('--timeout',
                    type=float,
                    default=71.9,
                    help='timeout in hours (default: 71.9 hours)'
)

parser.add_argument('--cluster',
                    type=str,
                    default='msi',
                    help='cluster to run on (default: msi)',choices=['msi','expanse','']
)

parser.add_argument('--env',
                    type=str,
                    default='nmma_env',
                    help='conda environment to run on (default: nmma_env)'
)

parser.add_argument('--dry-run',
                    action='store_true',
                    help='dry run, do not submit jobs'
)

parser.add_argument('--nmma-tmin',
                    type=float,
                    default=0.1,
                    help='tmin value to use for analysis of all light curves (default: 0.1)'
)
parser.add_argument('--nmma-plot',
                    action='store_true',
                    help='whether to plot the nmma fits with nmma'
)
                    

args = parser.parse_args()
priors = args.priors
datadir = args.data
models = args.models
outdir = args.outdir
timeout = args.timeout
cluster = args.cluster if args.cluster != '' else False
env = args.env
tmin = args.tmin
tmax = args.tmax
tstep = args.tstep
nmma_tmin = args.nmma_tmin
nmma_plot = args.nmma_plot

# if os.path.exists(outdir):
#     print('outdir already exists, are you sure you want to overwrite? adding timestamp to outdir just in case')
#     outdir = os.path.join(outdir +'-'+ strtime())
#     print(f'outdir is now {outdir}')

os.makedirs(outdir, exist_ok=True)


lightcurve_paths = sorted(glob.glob(os.path.join(datadir,'lc*.json'))) ## assumes leading label is lc_
lightcurve_labels = [os.path.basename(lc).split('.')[0]for lc in lightcurve_paths] ## assumes leading label is lc_

tmax_array = np.arange(tmin,tmax,tstep)

estimated_job_count = len(lightcurve_paths) * len(models) * len(tmax_array)
if cluster=='expanse' and estimated_job_count > 4096 and not args.dry_run or cluster=='msi' and estimated_job_count > 2000 and not args.dry_run:
    print(f'warning: estimated job count exceeds the limit for {cluster} (estimated job count: {estimated_job_count})')
    while True:
        user_input = input('continue? (y/n)')
        if user_input == 'y' or user_input == 'yes':
            break
        elif user_input == 'n' or user_input == 'no':
            exit()
        else:
            print('invalid input, try again')

results_paths = []
bestfit_paths = []
start_time = time.time() ## start of submission process
for model in models:
    model_prior = os.path.join(priors,f'{model}.prior')
    for lightcurve_path in lightcurve_paths:
        # lightcurve_label = os.path.basename(lightcurve_path).split('.')[0]
        # print(f'running analysis on {lightcurve_label} with {model} model')
        idx_results_paths, idx_bestfit_paths = timestep_lightcurve_analysis(lightcurve_path, model, model_prior, outdir, label=None, tmax_array=tmax_array, slurm=cluster, dry_run=args.dry_run, env=env,nmma_tmin=nmma_tmin, nmma_plot=nmma_plot)
        results_paths += idx_results_paths
        bestfit_paths += idx_bestfit_paths

submission_time = time.time() ## all submissions made
print(f'all fits submitted (submission took {submission_time-start_time//3600} hours and {((submission_time-start_time)%3600)//60} minutes elapsed)')
while True:
    if args.dry_run:
        print('dry run complete, exiting')
        break
    completion_bool, completed_fits = check_completion(result_paths=results_paths, t0=start_time, t0_submission=submission_time, timeout=timeout)
    if completion_bool:
        end_time = time.time()
        print(f'completed all fits in {end_time-start_time//3600} hours and {((end_time-start_time)%3600)//60} minutes')
        break
    time.sleep(120)