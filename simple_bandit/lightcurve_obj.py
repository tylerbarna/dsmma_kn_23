import numpy as np
import os

class LightCurve:

    def __init__(self, path, models, priors, n_obs):
        
        self.path = path
        self.models = models
        self.priors = priors
        self.mask = np.zeros(n_obs)

    def get_priors(self, model):

        model_prior = os.path.join(self.priors, f'{model}.prior')

    def compute_models(self, outdir):

        for model in self.models:

            model_prior = self.get_priors(model)

            # compute lightcurve models for each prior

            # idx_results_path, idx_bestfit_paths = timestep_lightcurve_analysis(self.path, model, model_prior, outdir, )

    def mask_lightcurve(mask, lc, model_n):
        '''
        Masks the true lightcurve so only the observed time-points have values.

        Assumptions: 
        - len(mask) == max len(lc). Since len(mask) = max(time), this should be true

        Args:
        - mask (dict): dictionary holding the timepoints where the object was observed (1) or not observed (0) {'ztfg': [1 1 0 1]}
        - lc (json): the true observations for the object in json format
        - model_n: name of the lightcurve model

        Returns:
        - No returns, saves masked lc to file 'lc_masked_{model_n}.json'
        '''

    for k in lc.keys():
            del_count = 0

            for i in range(len(lc[k])):
                if mask[k][i] == 0:
                    del lc[k][i - del_count]
                    del_count += 1

    masked_file = open(f"lc_masked_{model_n}.json", "w")
    json.dump(lc, masked_file, indent = 6)
    masked_file.close()

    def mask(self, idx):
        
        self.mask[idx] = 1

