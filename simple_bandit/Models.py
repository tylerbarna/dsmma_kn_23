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
###################################################################################################
class Models:

    def __init__(self, models, priors):

        self.model_names = models

        self.priors = priors

        self.model_prior_paths = []    # CHECK need list or?

        # get path to model priors
        for model in self.model_names:
            model_prior = os.path.join(self.priors, f'{model}.prior')
            self.model_prior_paths.append(model_prior)

    def run_models(self, lc):
        pass
        
        model_fits_results = {}

        for model, prior in zip(self.model_names, self.priors):
            label = 'ADD'
            results_path, bestfit_path = lightcurve_analysis(lc, model, prior, outdir= None, label= label)

            bestfit_file = open(bestfit_path)
            best_fit_json = json.load(bestfit_file)
            bestfit_file.close()

            model_fits_results[model] = {"log_likelihood": best_fit_json["log_likelihood"],
                                         "log_bayes_factor": best_fit_json["log_bayes_factor"]}


        # run lightcurve analysis for all models for the given lightcurve lc
        # generate a dictionary for the info we want (BF, residuals, likelihood, etc.)
        # return the dictionary 
        # while loop to wait until you get all the model fits for all the 

        # dict: {modelA : {"log_bayes": 0, 
        #                 "likelihood": 0}
        #        modelB : {"log_bayes": 0, 
        #                 "likelihood": 0}
        #        }

        