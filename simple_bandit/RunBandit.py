import argparse
import glob
import json
import numpy as np
import os
import time

import sys #############################################################
sys.path.append('~/dsmma_kn_23') #############################################################

from concurrent.futures import ProcessPoolExecutor

from pathlib import Path

from BanditUtils import find_start_time

parser = argparse.ArgumentParser(description='Do analysis on light curves')

parser.add_argument('-m','--models', 
                    type=str, nargs='+', 
                    default=['nugent-hyper','Me2017','TrPi2018'],
                    choices=['nugent-hyper','Bu2019lm','TrPi2018', 'Me2017', 'Piro2021'], 
                    help='models to generate light curves for'
)

parser.add_argument('-tm', '--target-model',
                    type=str,
                    default='Me2017',
                    choices=['nugent-hyper','Bu2019lm','TrPi2018', 'Me2017', 'Piro2021'], 
                    help='model to use as the target for the bandit'
                    )
# parser.add_argument('-f','--filters',
#                     type=str,
#                     default='g',
#                     help='filters to generate light curves for (choices for ztf are ztfr,ztfg,ztfi)'
# )

parser.add_argument('-stat', '--target-statistic',
                    type=str,
                    default='log_likelihood',
                    choices=['log_likelihood','log_bayes_factor'],
                    help='statistic to use for reward in bandit'
)

parser.add_argument('-p','--priors',
                    type=str,
                    default='/home/tbarna/dsmma_kn_23/priors',
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

parser.add_argument('--nsteps',
                    type=int,
                    default=4,
                    help='number of intervals to use for bandit (default: 4)'
)

parser.add_argument('--outdir',
                    type=str,
                    default='./fits',
                    help='path to output directory'
)

parser.add_argument('--clean-run',
                    action='store_true',
                    help='delete all files and folders that start with observed_ in the outdir')

parser.add_argument('--timeout',
                    type=float,
                    default=1,
                    help='timeout in hours (default: 1 hours)'
)

parser.add_argument('--cluster',
                    type=str,
                    default='expanse',
                    help='cluster to run on (default: expanse)',choices=['msi','expanse','']
)

parser.add_argument('--env',
                    type=str,
                    default='nmma_dev',
                    help='conda environment to run on (default: nmma_dev)'
)

parser.add_argument('--dry-run',
                    action='store_true',
                    help='dry run, do not submit jobs'
)

args = parser.parse_args()
priors = args.priors
datadir = args.data
models = args.models
target_model = args.target_model
outdir = args.outdir
clean_run = args.clean_run
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
if clean_run:
    print(f'cleaning run, deleting all files and folders that start with observed_ in {outdir}')
    os.system(f'rm -r {os.path.join(outdir, "observed_*")}')

os.makedirs(outdir, exist_ok=True)


lightcurve_paths = sorted(glob.glob(os.path.join(datadir,'lc*.json'))) ## assumes leading label is lc_
lightcurve_labels = [os.path.basename(lc).split('.')[0]for lc in lightcurve_paths] ## assumes leading label is lc_

# tmax_array = np.arange(tmin,tmax,tstep)

# estimated_job_count = len(lightcurve_paths) * len(models) * len(tmax_array)
# if estimated_job_count > 4096 and not args.dry_run:
#     print('warning: estimated job count exceeds 4096, this may exceed the limits for job counts on expanse')
#     while True:
#         user_input = input('continue? (y/n)')
#         if user_input == 'y' or user_input == 'yes':
#             break
#         elif user_input == 'n' or user_input == 'no':
#             exit()
#         else:
#             print('invalid input, try again')

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
model_of_interest = target_model

if model_of_interest not in models:
    raise ValueError(f'model_of_interest: {model_of_interest} not in models: {models}')

# (str) - name of statistic you want to use to compute reward (CURRENTLY just: 'likelihood' or 'log_bayes')
stat_to_use = args.target_statistic

# (float) - the latest time observation for all the candidate objects
#init_time = 3.1  #TODO: make a function to find the initial time, when we want bandit to take over
init_time = find_start_time(lightcurve_paths, min_detections=3, all_filters=False)
          
# (float) - the length of time you want each observation interval to be
time_step = 1.0

# (int) - the number of intervals you want the bandit to choose objects for
n_steps = args.nsteps

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
# lc_idx = 0
lc_array = [*range(n_objects)]
init_reward_array = []

def init_observation(lightcurve_path, lc_idx):
    new_lc = LightCurve(lightcurve_path, n_intervals, sim, all_models)
    model_fits = new_lc.observe_lightcurve(0, intervals[0][0], intervals[0][1]) # CHECK
    reward = stochastic_reward(model_fits, model_of_interest, stat_to_use)
    Bandit.initial_reward(lc_idx, reward)
    #init_reward_array[lc_idx] = reward
    print(f'{lightcurve_path} ({lc_idx}) initial reward is {reward}')
    return (new_lc, reward)

with ProcessPoolExecutor() as executor:
    for out in executor.map(init_observation, lightcurve_paths, lc_array):
        lc, r = out
        lightcurve_objects.append(lc)
        init_reward_array.append(r)
        #lc_idx += 1
[print(f'init_reward_array: {init_reward_array}')]
[Bandit.initial_reward(i, init_reward_array[i]) for i in range(n_objects)]
for i in range(n_objects):
    print('initial rewards are ', Bandit.obj_rewards[i])

# for lightcurve_path in lightcurve_paths:

#     # initialize LC object
#     new_lc = LightCurve(lightcurve_path, n_intervals, sim, all_models)

#     # get initial obs and corresponding reward
#     model_fits = new_lc.observe_lightcurve(0, intervals[0][0], intervals[0][1]) # CHECK
#     print(f'model fits: {model_fits}')
#     reward = stochastic_reward(model_fits, model_of_interest, stat_to_use)

#     # add initial reward to bandit
#     Bandit.initial_reward(lc_idx, reward)

#     lightcurve_objects.append(new_lc)
#     lc_idx += 1

    # print(f'model fits: {model_fits}')
    # print(f'reward: {reward}')
# print('Initialized lightcurves Complete')
    
'''5. Run bandit'''
print(f'Running bandit for {n_intervals}')
for obs_int in range(n_intervals-1):  ### For online data, this would have to have a time check
    
    
    ## find all subfolders of the outdir that start with pm_ and delete them. these folders can be multiple levels deep
    # pm_folders = glob.glob(os.path.join(outdir, '**/pm_*')) ## this doesn't work
    pm_folders = glob.glob(os.path.join(outdir, '**','pm_*'))
    
    print(f'pm_folders: {pm_folders}')
    for folder in pm_folders:
        ## define name of folder that the pm_ folder is in
        containing_folder = os.path.dirname(folder)
        best_fit_params = [f for f in os.listdir(folder) if 'bestfit_params' in f]
        ## copy bestfit_params files into one level above containing folder, appending the current time to them to avoid overwriting
        [os.system(f'cp {os.path.join(folder, f)} {os.path.join(os.path.dirname(containing_folder), Path(f).stem)}_{time.time()}.json') for f in best_fit_params]
        print(f'rm -r {folder}')
        os.system(f'rm -r {folder}')
    posterior_samples = glob.glob(os.path.join(outdir, '**','*posterior_samples.dat'))
    print(f'posterior_samples: {posterior_samples}')
    [os.system(f'rm {f}') for f in posterior_samples]
    os.system("find "+outdir+" -type d -name 'pm_*' -prune -exec rm -rf {} +")
    os.system("find "+outdir+" -type d -name '*posterior_samples.dat' -prune -exec rm -rf {} +")
    time.sleep(1)

        
    print(f'\n\nObservation interval {obs_int + 1} starting:')

    int_start_t = intervals[obs_int + 1][0]
    int_end_t = intervals[obs_int + 1][1]    

    # choose lc to observe
    chosen_object_idx = Bandit.choose_obj()     # the Bandit returns the index of the object with the highest reward
    chosen_object = lightcurve_objects[chosen_object_idx]
    print('chosen object: ', chosen_object.label)
    print(type(chosen_object))

    # observe lc and get reward
    model_fits = chosen_object.observe_lightcurve(obs_int + 1, int_start_t, int_end_t)  # add one to idx because initial obs are in 0-th place
    reward = stochastic_reward(model_fits, model_of_interest, stat_to_use)
    ## delete all folders that start with pm_ in all subdirectories of the outdir
    
    # pm_folders = glob.glob(os.path.join(outdir, '**/pm_*'))
    # for folder in pm_folders:
    #     os.system(f'rm -r {folder}')
    
    # update bandit with new reward
    Bandit.update_model(reward)
    os.system("find "+outdir+" -type d -name 'pm_*' -prune -exec rm -rf {} +")
    os.system("find "+outdir+" -type d -name '*posterior_samples.dat' -prune -exec rm -rf {} +")
    
    
print('Bandit run complete')
stopTime = time.time()

fit_stats_file = os.path.join(outdir, 'fit_stats.json')
fit_stats_dict = {lightcurve_labels[i]: lightcurve_objects[i].fit_stats for i in range(n_objects)}
fit_stats_dict['misc'] = {'start_time': start_time, 'end_time': stopTime, 'run_time': stopTime - start_time}
with open(fit_stats_file, 'w') as f:
    json.dump(fit_stats_dict, f, indent=6)

print('bandit reward values:')
for i in range(n_objects):
    print(f'{lightcurve_labels[i]} reward: {Bandit.obj_rewards[i]}')
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