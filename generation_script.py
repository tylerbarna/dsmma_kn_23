import argparse
import numpy as np
import os
import time
import multiprocessing
import threading

from multiprocessing import Pool
from utils.injections import generate_injection
from utils.lightcurves import generate_lightcurve, validate_lightcurve
from utils.misc import strtime

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

def generate_lightcurves_for_model(model, multiplier, validate, min_detections, min_detections_cuttoff, filters, ztf_sampling, plot, time_series, outdir, start_idx):
    print(f'[{strtime()}] starting model: {model}')
    lc_count = 1 * multiplier

    for lc_idx in range(start_idx, start_idx + lc_count):
        generated_lc = False
        lc_idx_zfill = str(lc_idx).zfill(5)
        retry_count = 0
        start_time = time.time()
        #print(f'[{strtime()}] generating light curve for {model}: {lc_idx_zfill}')
        while not generated_lc:
            try:
                #print('\nattempt {0}'.format(retry_count))
                injection_file = generate_injection(model=model, outDir=outdir, injection_label=lc_idx_zfill)
                #print('created injection file: {0}'.format(injection_file))
                lightcurve_file = generate_lightcurve(model=model, injection_path=injection_file, outDir=outdir, filters=filters, time_series=time_series, ztf_sampling=ztf_sampling, plot=plot)
                assert os.path.exists(lightcurve_file), "light curve file {} does not exist".format(lightcurve_file)
                if validate:
                    assert validate_lightcurve(lightcurve_file, min_detections=min_detections, min_time=min_detections_cuttoff), "light curve validation failed"
                generated_lc = True
            except Exception as e:
                retry_count += 1
                #print('generation error: {0}'.format(e))
                try:
                    os.remove(injection_file), os.remove(lightcurve_file)
                except:
                    pass
                pass
        end_time = time.time()
        elapsed_hours, elapsed_rem = divmod(end_time - start_time, 3600)
        elapsed_mins = elapsed_rem // 60
        print(f'succsefully generated {lightcurve_file} in {elapsed_hours:.0f}:{str(elapsed_mins).zfill(2)} hours (took {retry_count} attempts)')

def main():
    parser = argparse.ArgumentParser(description='Generate light curves for a given model')
    parser.add_argument('-m', '--models', type=str, nargs='+', default=['nugent-hyper', 'Bu2019lm', 'TrPi2018', 'Piro2021'],
                        choices=['nugent-hyper', 'Bu2019lm', 'TrPi2018', 'Me2017', 'Piro2021'],
                        help='models to generate light curves for')
    parser.add_argument('-p', '--priors', type=str, default='~/dsmma_kn_23/priors',
                        help='path to the prior files (default=~/dsmma_kn_23/priors)')
    parser.add_argument('-f', '--filters', type=str, nargs='+', default='ztfg',
                        choices=['ztfr', 'ztfg', 'ztfi'],
                        help='filters to generate light curves for (choices for ztf are r, g, i)')
    parser.add_argument('-o', '--outdir', type=str, default='./injections/',
                        help='output directory for light curves')
    parser.add_argument('--no-validate', action='store_false',
                        help='whether to validate the light curves (default=true). When true, will attempt to resample injection until a valid light curve is generated.')
    parser.add_argument('--min-detections', type=int, default=3,
                        help='minimum number of detections required for a light curve to be considered valid (default=3)')
    parser.add_argument('--min-detections-cutoff', type=float, default=3.1,
                        help='time after start of lightcurve to consider points for when validating (default=3.1)')
    parser.add_argument('--cadence', type=float, default=0.5,
                        help='cadence of light curve (default=0.5)')
    parser.add_argument('--multiplier', type=int, default=1,
                        help='multiplier for the number of light curves to generate (default=1)')
    parser.add_argument('--ztf-sampling', action='store_true',
                        help='whether to use ztf sampling (default=False)')
    parser.add_argument('--plot', action='store_true',
                        help='whether to plot the light curve (default=False)')
    parser.add_argument('--start-idx', type=int, default=0,
                        help='the starting index for the generated light curves')
    parser.add_argument('--parallel', action='store_true',
                        help='whether to use parallelization (default=False)')
    args = parser.parse_args()
    models = args.models
    outdir = args.outdir
    multiplier = args.multiplier
    validate = args.no_validate
    min_detections = args.min_detections
    min_detections_cuttoff = args.min_detections_cutoff
    filters = [args.filters] if type(args.filters) == str else args.filters
    ztf_sampling = args.ztf_sampling
    plot = args.plot
    start_idx = args.start_idx
    os.makedirs(outdir, exist_ok=True)
    priors = [os.path.join(args.priors, model + '.prior') for model in models]
    inj_gen_time_dict = {model: [] for model in models}
    time_series = np.arange(0.01, 20.0 + 0.5, args.cadence)
    start_time = time.time()
    if args.parallel:
        with Pool() as pool:
            for lc_idx in range(start_idx, start_idx + 1 * multiplier):
                # pool.apply_async(generate_lightcurves_for_model, args=(model, multiplier, validate, min_detections, min_detections_cuttoff, filters, ztf_sampling, plot, time_series, outdir, start_idx))
                    for model in models:
                        lc_idx_zfill = str(lc_idx).zfill(5)
                        pool.apply_async(generate_lightcurves_for_model, args=(model, 1, validate, min_detections, min_detections_cuttoff, filters, ztf_sampling, plot, time_series, outdir, lc_idx)) ## multiplier set to 1 so that each process only generates one light curve with the appropiate index value
                    # pool.apply_async(generate_lightcurve, args=(model, injection_file, outdir, filters, time_series, ztf_sampling, plot))
            pool.close()
            pool.join()
    else:
        for model in models:
            generate_lightcurves_for_model(model, multiplier, validate, min_detections, min_detections_cuttoff, filters, ztf_sampling, plot, time_series, outdir, start_idx)
    end_time = time.time()
    # get hours and minutes
    elapsed_hours, elapsed_rem = divmod(end_time - start_time, 3600)
    elapsed_mins = elapsed_rem // 60
    print(f'[{strtime()}] finished generating all light curves')
    print(f'[{strtime()}] total time elapsed: {elapsed_hours:.0f} hours, {elapsed_mins:.0f} minutes')

if __name__ == '__main__':
    main()
