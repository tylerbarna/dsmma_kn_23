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
                    default=['nugent-hyper','Me2017','TrPi2018'],
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

# if os.path.exists(outdir):
#     print('outdir already exists, are you sure you want to overwrite? adding timestamp to outdir just in case')
#     outdir = os.path.join(outdir +'-'+ strtime())
#     print(f'outdir is now {outdir}')

os.makedirs(outdir, exist_ok=True)


lightcurve_paths = sorted(glob.glob(os.path.join(datadir,'lc*.json'))) ## assumes leading label is lc_
lightcurve_labels = [os.path.basename(lc).split('.')[0]for lc in lightcurve_paths] ## assumes leading label is lc_

tmax_array = np.arange(tmin,tmax,tstep)

estimated_job_count = len(lightcurve_paths) * len(models) * len(tmax_array)
if estimated_job_count > 4096 and not args.dry_run:
    print('warning: estimated job count exceeds 4096, this may exceed the limits for job counts on expanse')
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


###################################################################################################
###################################################################################################
# Run Multi-Arm Bandit 
###################################################################################################
'''
Multi-arm bandit steps:
- initiate multi-arm bandit class
- at each time point in tmax_array, have the multi-arm bandit decide what lc to observe
- update each lc's rewards
'''
from simple_bandit.MultiArmBandit import UCB
from simple_bandit.LightCurve import LightCurve

from simple_bandit.BanditUtils import get_intervals
from simple_bandit.Rewards import stochastic_reward

# Boolean - declare True if simulation, False if online data
sim = True


# calculate the intervals we want our bandit to use
intervals = get_intervals(init_time = 0.0, time_step = 2.0)  # CHECK where get info for this?
n_intervals = len(intervals) # CHECK


### ADD the initial run of the lightcurves here...like the while-loop check??
# create lightcurve objects for all candidate lightcurves
lightcurve_objects = []
for lightcurve_path in lightcurve_paths:

    new_lc = LightCurve(lightcurve_path, n_intervals, sim)

    lightcurve_objects.append(new_lc)

# instantiate bandit
n_objects = len(lightcurve_objects)   # CHECK
Bandit = UCB(n_objects)


# Initial chosen object is the object with thei highest reward
chosen_object_idx = Bandit.choose_obj()    # this object is the one that the bandit will tell NMMA to choose
chosen_object = lightcurve_objects[chosen_object_idx]

# Run bandit

for obs_int in range(n_intervals):  ### For online data, this would have to have a time check

    int_start_t = intervals[obs_int][0]     # CHECK
    int_end_t = intervals[obs_int][1]       # CHECK

    # DONT NEED THIS INITIAL CASE ANYMORE
    if obs_int == 0:
        # MOVE to creation of ligthcurve objects: have to observe and generate reward for all lc objects
        # while loop that checks if they're all done --- do we need this here???

        for obj_idx in range(n_objects):    # CHECK
            lc = lightcurve_objects[obj_idx]
            model_fits = lc.observe_lightcurve(obs_int, int_start_t, int_end_t)     # get initial model fits using initial observations
            reward = stochastic_reward(model_fits)      # calculate the reward for an object
            Bandit.initial_reward(obj_idx, reward)      # give this initial reward to the Bandit
        ## end MOVE

        # DONT NEED THIS ANYMORE, CHOSE FIRST OBJECT OUTSIDE OF FOR LOOP
        chosen_object_idx = Bandit.choose_obj()     # the Bandit returns the index of the object with the highest reward
        chosen_object = lightcurve_objects[chosen_object_idx]

    else:

        model_fits = chosen_object.observe_lightcurve(obs_int, int_start_t, int_end_t)  # observe the current chosen_object and get its model fits
        
        reward = stochastic_reward(model_fits)
        Bandit.update_model(reward)
        
        chosen_object_idx = Bandit.choose_obj()
        chosen_object = lightcurve_objects[chosen_object_idx]

############## do this in Models.py ########################
# for model in models:
#     model_prior = os.path.join(priors,f'{model}.prior')
#     for lightcurve_path in lightcurve_paths:
#         # lightcurve_label = os.path.basename(lightcurve_path).split('.')[0]
#         # print(f'running analysis on {lightcurve_label} with {model} model')
#         idx_results_paths, idx_bestfit_paths = timestep_lightcurve_analysis(lightcurve_path, model, model_prior, outdir, label=None, tmax_array=tmax_array, slurm=cluster, dry_run=args.dry_run, env=env)
#         results_paths += idx_results_paths
#         bestfit_paths += idx_bestfit_paths

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