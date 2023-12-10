###################################################################################################
###################################################################################################
# imports
###################################################################################################
import os
import json

from utils.analysis import lightcurve_analysis
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

    def run_models(self, lc, outdir):
        ''' given lightcurve file path, run model fits for all models being considered. Save stats for each model'''
        model_fits_results = {}

        # TODO: while loop to wait until you get all the model fits for all the 

        for model, prior in zip(self.model_names, self.priors):
            
            # code edited from analysis.py function: timestep_lightcurve_analysis
            lightcurve_label = os.path.basename(lc).split('.')[0]
            lighcurve_outdir = os.path.join(outdir, lightcurve_label)
            model_outdir = os.path.join(lighcurve_outdir, model) ## so directory structure will be {outdir}/{lightcurve_label}/{model}/
            os.makedirs(model_outdir, exist_ok=True)
            fit_label = lightcurve_label + '_fit_' + model 
            
            results_path, bestfit_path = lightcurve_analysis(lc, model, prior, outdir= model_outdir, label= fit_label)  # this will override the previous run

            bestfit_file = open(bestfit_path)
            best_fit_json = json.load(bestfit_file)
            bestfit_file.close()

            model_fits_results[model] = {"log_likelihood": best_fit_json["log_likelihood"],
                                         "log_bayes_factor": best_fit_json["log_bayes_factor"]}

        return model_fits_results


        