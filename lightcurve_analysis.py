import subprocess
import sys
import os
import argparse
from pathlib import Path
import time

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
parser.add_argument("--outdir", type=str, default="/home/cough052/barna314/dsmma_kn_23/fits", help="Path to the output directory")

args = parser.parse_args()

outdir_base = os.path.join(args.outdir, args.candname)

os.path.exists(outdir_base) or os.makedirs(outdir_base)

lc_path = args.datafile

cand = args.candname

model = args.model

svdmodels = args.svdmodels

prior = args.prior

filters = 'g'


## will probably need to tweak based on final version of the ingest data
df = pd.read_csv(lc_path, sep="\s+", header=None, names=['time','filter','mag','magerr'])

df['time'] = [Time(t, format='isot') for t in df['time']]
trigger_time = df['time'][0].mjd
time_range = np.arange(3.01, 15.01, 2)
    #[t.mjd +0.01 for t in df['time']]

## do whatver time conversion required (may be ingested as isot)
# time_range = df['time'].mjd + 0.01 ## set max time slightly above each data point to go point by point

# outdir_array = np.empty(len(time_range))
for idx, tmax in enumerate(time_range):
    # outdir_array[idx] = os.path.join(outdir_base,)
    # outdir_iter = outdir_array[idx]
    # os.path.exists(outdir_iter) or os.makedirs(outdir_iter)
    label = '{}_t_{}'.format(cand, int(tmax))
    print('starting analysis for {}'.format(label))
    cmd_str = [#'mpiexec -np',str(args.cpus),
               'light_curve_analysis',
               '--data', lc_path,
               '--model', model,
               '--label', label,
               '--prior', prior,
               '--svd-path', svdmodels,
                '--filters', filters,
                '--tmin', '0.1',
                '--tmax', str(tmax),
                '--dt', '0.5',
                '--trigger-time', str(trigger_time),
                '--error-budget', '1',
                '--nlive', str(args.nlive),
                '--remove-nondetections',
                '--ztf-uncertainties',
                #'--ztf-sampling',
                '--ztf-ToO', '180',
                '--outdir', outdir_base,
                '--plot', 
                '--verbose',
                " --detection-limit \"{\'r\':21.5, \'g\':21.5, \'i\':21.5}\""
                ]
    command = ' '.join(cmd_str)
    print('command: {}'.format(command))
    subp = subprocess.run(command, shell=True, capture_output=True)#, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
    ## do I want to run them all sequentially? Would probably be fine to run them in sequence since I'll submit each object/model seperately
    pewda = os.path.join(outdir_base, label, 'pm_'+label,'post_equal_weights.da')
    pewdat = os.path.join(outdir_base, label, 'pm_'+label,'post_equal_weights.dat')
    if os.path.isfile(pewda):
        os.rename(pewda, pewdat)
    #sys.stdout.buffer.write(subp.stdout)
    sys.stderr.buffer.write(subp.stderr)
    print("({}) executing: {}".format(time.ctime(), command))
    #stdout, stderr = subp.communicate() ## unsure about this
    # try: ## this may not work? Need to check if it waits properly
    #     Path('lightcurve.png').rename(os.path.join(outdir_iter,'lightcurve.png'))
    # except:
    #     print('No lightcurve.png found')


    ## lightcurves will output to cwd I think, might need to pr nmma to correct label functionality





