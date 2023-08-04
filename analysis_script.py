import argparse
import glob
import os
import time

from utils.analysis import timestep_lightcurve_analysis, check_completion
from utils.misc import strtime

parser = argparse.ArgumentParser(description='Do analysis on light curves')


parser.add_argument('-m','--models', 
                    type=str, nargs='+', 
                    default=['nugent-hyper','Bu2019lm','TrPi2018'], 
                    help='models to generate light curves for'
)
# parser.add_argument('-f','--filters',
#                     type=str,
#                     default='g',
#                     help='filters to generate light curves for (choices for ztf are ztfr,ztfg,ztfi)'
# )

parser.add_argument('-p','--priors',
                    type=str,
                    default='./priors',
                    help='path to the prior files'
)

parser.add_argument('--data',
                    type=str,
                    required=True,
                    help='path to lightcurves'
)

parser.add_argument('--outdir',
                    type=str,
                    default='./fits',
                    help='path to output directory'
)

parser.add_argument('--timeout',
                    type=float,
                    default=71.9,
                    help='timeout in hours (default: 71.9 hours)')


args = parser.parse_args()
priors = args.priors
datadir = args.data
models = args.models
outdir = args.outdir
timeout = args.timeout

if os.path.exists(outdir):
    print('outdir already exists, are you sure you want to overwrite? adding timestamp to outdir just in case')
    outdir = os.path.join(outdir +'('+ strtime()+')')
    print(f'outdir is now {outdir}')

os.makedirs(outdir)


lightcurve_paths = sorted(glob.glob(os.path.join(datadir,'lc*.json'))) ## assumes leading label is lc_
lightcurve_labels = [os.path.basename(lc).split('.')[0]for lc in lightcurve_paths] ## assumes leading label is lc_

results_paths = []
bestfit_paths = []
for model in models:
    model_prior = os.path.join(priors,f'{model}.prior')
    for lightcurve_path in lightcurve_paths:
        # lightcurve_label = os.path.basename(lightcurve_path).split('.')[0]
        # print(f'running analysis on {lightcurve_label} with {model} model')
        idx_results_paths, idx_bestfit_paths = timestep_lightcurve_analysis(lightcurve_path, model, model_prior, outdir, label=None, tmax_array=None, threading=True)
        results_paths += idx_results_paths
        bestfit_paths += idx_bestfit_paths

print('all fits submitted, checking for completion')
start_time = time.time()
while True:
    time.sleep(300)
    completion_bool, completed_fits = check_completion(results_paths, start_time, timeout)
    if completion_bool:
        break

