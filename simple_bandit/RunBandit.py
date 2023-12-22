import argparse
import glob
import numpy as np
import os
import time

import sys #############################################################
sys.path.append('~/dsmma_kn_23') #############################################################

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
                    default='expanse',
                    help='cluster to run on (default: expanse)',choices=['msi','expanse','']
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
# imports
###################################################################################################
from MultiArmBandit import UCB
from LightCurve import LightCurve
from Models import Models

from BanditUtils import get_intervals
from Rewards import stochastic_reward
###################################################################################################

###################################################################################################
###################################################################################################
# Run Multi-Arm Bandit:
# - 1. declare variables
# - 2. calculate the intervals we want our bandit to use
# - 3. instantiate bandit object 
# - 4. create lightcurve objects for all candidate lightcurves
# - 5. run bandit
###################################################################################################

'''1. Declare variables'''
# (Boolean) - declare True if simulation, False if online data
sim = True

# (str) - name of object of interest (the type of model we want the bandit to observe)
model_of_interest = 'Me2017'

# (str) - name of statistic you want to use to compute reward (CURRENTLY just: 'likelihood' or 'log_bayes')
stat_to_use = 'log_likelihood'

# (float) - the latest time observation for all the candidate objects
init_time = 44245
          
# (float) - the length of time you want each observation interval to be
time_step = 1.0

# (int) - the number of intervals you want the bandit to choose objects for
n_steps = 10

# Models object
all_models = Models(models, priors)
print(f'All models: {models, priors}')

'''2. calculate the intervals we want our bandit to use'''
intervals = get_intervals(init_time, time_step, n_steps)
n_intervals = len(intervals)
print(intervals)

'''3. instantiate bandit object'''
n_objects = len(lightcurve_paths)
Bandit = UCB(n_objects)

### CHECK: ok that while loop only in run_models (called by observe_lightcurve)

'''4. create lightcurve objects for all candidate lightcurves'''
lightcurve_objects = []
lc_idx = 0

for lightcurve_path in lightcurve_paths:

    # initialize LC object
    new_lc = LightCurve(lightcurve_path, n_intervals, sim, all_models)

    # get initial obs and corresponding reward
    model_fits = new_lc.observe_lightcurve(0, intervals[0][0], intervals[0][1]) # CHECK
    print(f'model fits: {model_fits}')
    reward = stochastic_reward(model_fits, model_of_interest, stat_to_use)

    # add initial reward to bandit
    Bandit.initial_reward(lc_idx, reward)

    lightcurve_objects.append(new_lc)
    lc_idx += 1

    # print(f'model fits: {model_fits}')
    # print(f'reward: {reward}')
# print('Initialized lightcurves Complete')
    
'''5. Run bandit'''
print(f'Running bandit for {n_intervals}')
for obs_int in range(n_intervals):  ### For online data, this would have to have a time check

    print(f'Observation interval {obs_int + 1} starting:')

    int_start_t = intervals[obs_int + 1][0]
    int_end_t = intervals[obs_int + 1][1]    

    # choose lc to observe
    chosen_object_idx = Bandit.choose_obj()     # the Bandit returns the index of the object with the highest reward
    chosen_object = lightcurve_objects[chosen_object_idx]

    # observe lc and get reward
    model_fits = chosen_object.observe_lightcurve(obs_int + 1, int_start_t, int_end_t)  # add one to idx because initial obs are in 0-th place
    reward = stochastic_reward(model_fits, model_of_interest, stat_to_use)
    
    # update bandit with new reward
    Bandit.update_model(reward)

##### NEED THIS HERE??
# submission_time = time.time() ## all submissions made
# print(f'all fits submitted (submission took {submission_time-start_time//3600} hours and {((submission_time-start_time)%3600)//60} minutes elapsed)')
# while True:
#     if args.dry_run:
#         print('dry run complete, exiting')
#         break
#     completion_bool, completed_fits = check_completion(result_paths=results_paths, t0=start_time, t0_submission=submission_time, timeout=timeout)
#     if completion_bool:
#         end_time = time.time()
#         print(f'completed all fits in {end_time-start_time//3600} hours and {((end_time-start_time)%3600)//60} minutes')
#         break
#     time.sleep(120)