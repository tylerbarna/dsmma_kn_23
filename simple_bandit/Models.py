###################################################################################################
###################################################################################################
# imports
###################################################################################################
import os


###################################################################################################
###################################################################################################
# Class: Models - contains the models and priors that will be considered,
#               - runs the models and returns a dictionary with the statistics for each model
###################################################################################################
class Models:

    def __init__(self, models, priors):

        self.model_names = models

        self.model_prior_paths = []    # CHECK need list or?

        # get path to model priors
        for model in self.model_names:
            model_prior = os.path.join(self.priors, f'{model}.prior')
            self.model_prior_paths.append(model_prior)

    def run_models(lc):
        pass
        # run lightcurve analysis for all models for the given lightcurve lc
        # generate a dictionary for the info we want (BF, residuals, likelihood, etc.)
        # return the dictionary 

        