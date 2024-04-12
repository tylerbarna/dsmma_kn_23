import argparse
import numpy as np
import os

from utils.injections import generate_injection
from utils.lightcurves import generate_lightcurve, validate_lightcurve
import multiprocessing
import concurrent.futures

parser = argparse.ArgumentParser(description="Generate light curves for a given model")

parser.add_argument(
    "-m",
    "--models",
    type=str,
    nargs="+",
    default=["nugent-hyper", "Me2017", "TrPi2018"],
    choices=["nugent-hyper", "Bu2019lm", "TrPi2018", "Me2017", "Piro2021"],
    help="models to generate light curves for",
)
parser.add_argument(
    "-f",
    "--filters",
    type=str,
    nargs="+",
    default="ztfg",
    choices=["ztfr", "ztfg", "ztfi"],
    help="filters to generate light curves for (choices for ztf are r,g,i)",
)

parser.add_argument(
    "-ztf",
    "--ztf-sampling",
    action="store_true",
    help="whether to use a ztf-like observing cadence for the light curves",
)

parser.add_argument(
    "-o",
    "--outdir",
    type=str,
    default="./injections/",
    help="output directory for light curves",
)

parser.add_argument(
    "--no-validate",
    action="store_false",
    help="whether to validate the light curves (default=true). When true, will attempt to resample injection until a valid light curve is generated.",
)

parser.add_argument(
    "--min-detections",
    type=int,
    default=3,
    help="minimum number of detections required for a light curve to be considered valid (default=3)",
)

parser.add_argument(
    "--min-detections-cutoff",
    type=float,
    default=3.1,
    help="time after start of lightcurve to consider points for when validating (default=3.1)",
)

parser.add_argument(
    "--retry-limit",
    type=int,
    default=1000,
    help="number of times to retry resampling injection before reducing minimum number of detections",
)

parser.add_argument(
    "--cadence", type=float, default=0.5, help="cadence of light curve (default=0.5)"
)

parser.add_argument(
    "--multiplier",
    type=int,
    default=1,
    help="multiplier for number of light curves to generate (default=1)",
)

parser.add_argument(
    "-i",
    "--index-offset",
    type=int,
    default=0,
    help="index offset for light curve generation (default=0)",
)

args = parser.parse_args()
models = args.models
outdir = args.outdir
multiplier = args.multiplier
validate = args.no_validate
min_detections = args.min_detections
min_detections_cuttoff = args.min_detections_cutoff
retry_limit = args.retry_limit
filters = [args.filters] if type(args.filters) == str else args.filters
ztf_sampling = args.ztf_sampling
idx_offset = args.index_offset
time_series = np.arange(0.01, 20.0 + 0.5, args.cadence)

os.makedirs(outdir, exist_ok=True)
priors = [os.path.join("./priors/", model + ".prior") for model in models]

inj_gen_time_dict = {model: [] for model in models}
injection_files = {model: [] for model in models}
lightcurve_files = {model: [] for model in models}


def generate_lightcurve_parallel(model, prior):
    print("\n\nstarting model: {0} with prior: {1}".format(model, prior))
    min_detections = args.min_detections  ## to reset from lessening of requirements
    if model == "nugent-hyper":
        lc_count = 7 * multiplier
    else:
        lc_count = 1 * multiplier

    for lc_idx in range(lc_count):
        lc_idx_zfill = str(lc_idx + idx_offset).zfill(5)  ## for ease of sorting
        try:
            print("\nstarting light curve: {0}".format(lc_idx_zfill))
            injection_file = generate_injection(
                model=model, outDir=outdir, injection_label=lc_idx_zfill
            )
            print("created injection file: {0}".format(injection_file))
            lightcurve_file = generate_lightcurve(
                model=model,
                injection_path=injection_file,
                outDir=outdir,
                filters=filters,
                time_series=time_series,
                lightcurve_label=lc_idx_zfill,
                ztf_sampling=ztf_sampling,
            )
        except Exception as e:
            injection_file, lightcurve_file = "", ""
            print("error when generating injected lightcurve:\n", e)
            pass
        if validate:
            retry_count = 1
            while not validate_lightcurve(
                lightcurve_file,
                min_detections=min_detections,
                min_time=min_detections_cuttoff,
            ):
                print("resampling injection (attempt {0})".format(retry_count))
                ## delete injection and light curve files
                os.remove(injection_file) if os.path.exists(injection_file) else None
                os.remove(lightcurve_file) if os.path.exists(lightcurve_file) else None
                try:
                    injection_file = generate_injection(
                        model=model, outDir=outdir, injection_label=lc_idx_zfill
                    )
                    # print('created injection file: {0}'.format(injection_file))
                    lightcurve_file = generate_lightcurve(
                        model=model,
                        injection_path=injection_file,
                        outDir=outdir,
                        filters=filters,
                        time_series=time_series,
                        lightcurve_label=lc_idx_zfill,
                        ztf_sampling=ztf_sampling,
                    )
                except:
                    pass
                retry_count += 1
                if retry_count >= retry_limit:
                    print(
                        f"Observation requirement is too strict, reducing minimum number of detections from {min_detections} to {min_detections-1}"
                    )
                    min_detections -= 1
                    retry_count = 1
                    if min_detections < 3:
                        print(
                            "Minimum number of detections has been reduced to 3, exiting (Note: you should probably take a look at that prior file or how many days the cutoff is set at)"
                        )
                        break
        injection_files[model].append(injection_file)
        lightcurve_files[model].append(lightcurve_file)


with concurrent.futures.ProcessPoolExecutor() as executor:
    executor.map(generate_lightcurve_parallel, models, priors)

# for model, prior in zip(models, priors):
#     generate_lightcurve_parallel(model, prior)
