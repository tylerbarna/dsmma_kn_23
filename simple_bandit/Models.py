###################################################################################################
###################################################################################################
# imports
###################################################################################################
import os
import json
import time
import shutil ############################################################# added for deleting directory 'pm_*'

import sys #############################################################
sys.path.append('home/tbarna/dsmma_kn_23') #############################################################
# sys.path.append('/Users/bean/Documents/Capstone/dsmma_kn_23') 

import sys  #####################################################################
from pathlib import Path  #####################################################################
sys.path.append(str(Path(__file__).parent.parent.parent))  #####################################################################
# rootpath = os.path.join(os.getcwd(), '..')
# sys.path.append(rootpath)
# sys.path.append(os.path.join(rootpath, 'utils'))
# sys.path.append('..')
# sys.path.append('../utils')
current_path = os.getcwd()  #####################################################################
#print(current_path)  #####################################################################
# os.chdir('../utils/')

# from utils.analysis import lightcurve analysis, check_completion  #####################################################################
from dsmma_kn_23.utils.analysis import lightcurve_analysis, check_completion  #####################################################################
#from utils.analysis import lightcurve_analysis, check_completion
# os.chdir(current_path)

from BanditUtils import lc_analysis_test
###################################################################################################
###################################################################################################
# Class: Models - contains the models and priors that will be considered,
#               - runs the models and returns a dictionary with the statistics for each model
#               - example dict: {
#                                   modelA : {"log_bayes": float, 
#                                             "likelihood": float},
#                                   modelB : {"log_bayes": float, 
#                                             "likelihood": float}
#                               }
###################################################################################################
class Models:
    '''
    Models class keeps models and priors chosen, runs model fits, and returns a dictionary with the statistics for each model

    Args:
    - models (str): list of models to consider
    - priors (str): path to the prior files
    '''
    def __init__(self, models, priors):

        self.model_names = models

        self.priors = priors

        self.model_prior_paths = []    # CHECK need list or?

        # get path to model priors
        for model in self.model_names:
            model_prior = os.path.join(self.priors, f'{model}.prior')
            self.model_prior_paths.append(model_prior)
            #print(f'prior path: {model_prior}')

    def run_models(self, lc, outdir):
        ''' given lightcurve file path, run model fits for all models being considered. Save stats for each model'''
        model_fits_results = {}

        best_fit_paths = []
        start_time = time.time()    # for the while loop to check all files are complete
        for model, prior in zip(self.model_names, self.model_prior_paths):
            #print('zip prior', prior)
            # code edited from analysis.py function: timestep_lightcurve_analysis
            lightcurve_label = os.path.basename(lc).split('.')[0]
            lighcurve_outdir = os.path.join(outdir, lightcurve_label)
            model_outdir = os.path.join(lighcurve_outdir, model) ## so directory structure will be {outdir}/{lightcurve_label}/{model}/
            os.makedirs(model_outdir, exist_ok=True)
            fit_label = lightcurve_label + '_fit_' + model 
            #print('model_outdir', model_outdir)
            
            

            # bestfit_path = lc_analysis_test(lc, model, prior, outdir = model_outdir, label = fit_label) ##################################################################### FOR TEST WITHOUT NMMA #####################################################################
            results_path, bestfit_path = lightcurve_analysis(lc, model, prior, outdir= model_outdir, label= fit_label, slurm = 'expanse')  # this will override the previous run
            best_fit_paths.append(bestfit_path)
            #print('bestfit_path', bestfit_path)
            #print('results_path', results_path)

        submission_time = time.time()   # for the while loop to check all files are complete
        
        # while loop to check all files are complete
        # code edited from analysis_script.py after timestep_ligthcurve_analysis is called
        while True:
            completion_bool, completed_fits = check_completion(best_fit_paths, t0 =start_time,  t0_submission= submission_time)
            if completion_bool:
                end_time = time.time()
                print(f'completed all fits in {((end_time-start_time)%3600)//60} minutes')
                break
            time.sleep(120)
        
        # now get the information from all the files
        for model, bestfit_path in zip(self.model_names, best_fit_paths):
            try: ## should account for any failed fits
                bestfit_file = open(bestfit_path)
                best_fit_json = json.load(bestfit_file)
                bestfit_file.close()
            except:
                print(f'failed to open {bestfit_path}, setting log_bayes and log_likelihood to -inf')
                best_fit_json = {"log_likelihood": -float('inf'), "log_bayes_factor": -float('inf')}

            model_fits_results[model] = {key:value for key, value in best_fit_json.items()}
            
            # delete any additional files created by previous lc fit before overwriting results_path and bestfit_path with lightcurve_analysis
            #############################################################
            dir_to_delete = 'pm_*'
            if os.path.exists(dir_to_delete):
                shutil.rmtree(dir_to_delete)
            #############################################################

        return model_fits_results

            