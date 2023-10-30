import argparse
import os

from utils.injections import generate_injection
from utils.lightcurves import generate_lightcurve, validate_lightcurve

parser = argparse.ArgumentParser(description='Generate light curves for a given model')

parser.add_argument('-m','--models', 
                    type=str, nargs='+', 
                    default=['nugent-hyper','Me2017','TrPi2018'],
                    choices=['nugent-hyper','Bu2019lm','TrPi2018', 'Me2017', 'Piro2021'], 
                    help='models to generate light curves for'
)
parser.add_argument('-f','--filters',
                    type=str, nargs='+',
                    default='ztfg',
                    choices=['ztfr','ztfg','ztfi'],
                    help='filters to generate light curves for (choices for ztf are r,g,i)'
)

parser.add_argument('-o','--outdir',
                    type=str,
                    default='./injections/',
                    help='output directory for light curves')

parser.add_argument('--no-validate',
                    action='store_false',
                    help='whether to validate the light curves (default=true). When true, will attempt to resample injection until a valid light curve is generated.')

parser.add_argument('--multiplier',
                    type=int,
                    default=1,
                    help='multiplier for number of light curves to generate (default=1)')


args = parser.parse_args()
models = args.models
outdir = args.outdir
multiplier = args.multiplier
validate = args.no_validate
filters = [args.filters] if type(args.filters) == str else args.filters

os.makedirs(outdir, exist_ok=True)
priors = [os.path.join('./priors/',model+'.prior') for model in models]

inj_gen_time_dict = {model:[] for model in models}

for model, prior in zip(models,priors):
    print('starting model: {0} with prior: {1}'.format(model,prior))
    if model == 'nugent-hyper':
        lc_count = 7 * multiplier
    else:
        lc_count = 1 * multiplier
    
    for lc_idx in range(lc_count):
        lc_idx_zfill = str(lc_idx).zfill(5) ## for ease of sorting
        print('starting light curve: {0}'.format(lc_idx))
        injection_file = generate_injection(model=model, outDir=outdir, injection_label=lc_idx_zfill)
        print('created injection file: {0}'.format(injection_file))
        lightcurve_file = generate_lightcurve(model=model, injection_path=injection_file, outDir=outdir, filters=filters)
        if validate:
            retry_count = 1
            while not validate_lightcurve(lightcurve_file):
                print('light curve validation failed, resampling injection (attempt {0})'.format(retry_count))
                ## delete injection and light curve files
                os.remove(injection_file), os.remove(lightcurve_file)
                injection_file = generate_injection(model=model, outDir=outdir, injection_label=lc_idx_zfill)
                print('created injection file: {0}'.format(injection_file))
                lightcurve_file = generate_lightcurve(model=model, injection_path=injection_file, outDir=outdir, filters=filters)
                retry_count += 1
        