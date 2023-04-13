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

args = parser.parse_args()
models = args.models
outdir = args.outdir

lc_paths = glob.glob(os.path.join(args.data,'*.dat')) ## list of lightcurve data files
lc_names = [os.path.basename(lc).split('.')[0].replace('lc_','') for lc in lc_paths] ## list of lightcurve names (eg nugent-hyper_0)
# print(lc_paths)
# print(lc_names)
#print(lightcurve_names)

for idx, lc in enumerate(lc_names):
    for model in models:

        prior = os.path.join(args.priors,model+'.prior')
        label = 'lc_{}_fit_{}'.format(lc,model)
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