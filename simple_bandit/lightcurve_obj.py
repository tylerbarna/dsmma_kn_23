import numpy as np
import os

class LightCurve:

    def __init__(self, path, models, priors):
        
        self.path = path
        self.models = models
        self.priors = priors

    def get_priors(self, model):

        model_prior = os.path.join(self.priors, f'{model}.prior')

    def compute_models(self, outdir):

        for model in self.models:

            model_prior = self.get_priors(model)

            # compute lightcurve models for each prior

            # idx_results_path, idx_bestfit_paths = timestep_lightcurve_analysis(self.path, model, model_prior, outdir, )
