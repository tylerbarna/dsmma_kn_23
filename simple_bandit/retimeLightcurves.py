## for a directory full of lightcurves, change the time values so all are started at t=0 relative to their first data point 

import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import glob
import time
import sys


## argparse the path to the lightcurves
parser = argparse.ArgumentParser(description='Do analysis on light curves')
parser.add_argument('--data', type=str, required=True, help='path to lightcurves')
parser.add_argument('--outdir', type=str, required=True, help='path to output directory')

args = parser.parse_args()

## get the lightcurves
lc_paths = sorted(glob.glob(os.path.join(args.data,'lc*.json')))

for lc in lc_paths:
    ## read in the lightcurve
    with open(lc, 'r') as f:
        lc_data = json.load(f)

    ## get the time values
    times = np.array(lc_data['ztfg'])[:,0]

    ## get the minimum time
    tmin = np.min(times)

    ## subtract tmin from all the time values
    for key in lc_data.keys():
        lc_data[key] = np.array(lc_data[key])
        lc_data[key][:,0] -= tmin
    ## need to go from ndarray back to list so it can be written to json
    lc_data['ztfg'] = lc_data['ztfg'].tolist()
    
    print(lc_data['ztfg']) #####################################################################
    ## write the new lightcurve to the output directory
    os.makedirs(args.outdir, exist_ok=True)
    outpath = os.path.join(args.outdir, os.path.basename(lc))
    with open(outpath, 'w') as f:
        json.dump(lc_data, f, indent=4)

    print(f'Wrote {outpath}')