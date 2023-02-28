import subprocess
import sys
import os
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

from astropy.time import Time
from matplotlib.pyplot import cm

# Command line args
parser = argparse.ArgumentParser(description="Inference on model parameters.")
parser.add_argument("--datafile", type=str, required=True, help="Path of the transient csv file")
parser.add_argument("--candname", type=str, required=True, help="Name of the transient")
parser.add_argument("--model", type=str, default='Bu2019lm', help="Name of the model to be used") 
parser.add_argument("--nlive", type=int, default=256, help="Number of live points to use")
parser.add_argument("--cpus", type=int, default=4, help="Number of cpus to use")
parser.add_argument("--svdmodels", type=str, default="/home/cough052/shared/NMMA/svdmodels", help="Path to the SVD models. Note: Not present in the repo, need to be aquired separately (Files are very large)")
parser.add_argument("--prior", type=str, default="/home/cough052/shared/NMMA/priors/Bu2019lm.prior", help="Path to the prior file")

args = parser.parse_args()

outdir_base = os.path.join('/panfs/roc/groups/7/cough052/barna314/dsmma_kn_23', args.candname)

os.path.exists(outdir_base) or os.makedirs(outdir_base)

lc_path = args.datafile

cand = args.candname

model = args.model

svdmodels = args.svdmodels

prior = args.prior

filters = 'g'


## will probably need to tweak based on final version of the ingest data
df = pd.read_csv(lc_path)
## do whatver time conversion required (may be ingested as isot)
time_range = df['time'] + 0.01 ## set max time slightly above each data point to go point by point

outdir_array = np.empty(len(time_range))
for tmax in time_range:
    outdir_array[tmax-1] = os.path.join(outdir_base+ '_tmax_'+str(tmax))
    outdir_iter = outdir_array[tmax-1]
    os.path.exists(outdir_iter) or os.makedirs(outdir_iter)
    cmd_str = ['mpiexec -np',str(args.cpus),
               'light_curve_analysis',
               '--model', model,
               '--label', cand,
               '--prior', prior,
                '--filters', filters,
                '--tmin', '0.1',
                '--tmax', str(tmax),
                '--dt', '0.5',
                '--error-budget', '1',
                '--nlive', str(args.nlive),
                '--remove-nondetections',
                '--ztf-uncertainties',
                '--ztf-sampling',
                '--ztf-ToO', '180',
                '--outdir', outdir_iter,
                '--plot', '--verbose'
                ]
    command = ' '.join(cmd_str)
    subp = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) ## do I want to run them all sequentially? Would probably be fine to run them in sequence since I'll submit each object/model seperately
    stdout, stderr = subp.communicate() ## unsure about this
    try: ## this may not work? Need to check if it waits properly
        Path('lightcurve.png').rename(os.path.join(outdir_iter,'lightcurve.png'))
    except:
        print('No lightcurve.png found')


    ## lightcurves will output to cwd I think, might need to pr nmma to correct label functionality





