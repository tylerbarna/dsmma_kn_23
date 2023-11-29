import numpy as np
import os
import json

class LightCurve:

    def __init__(self, path, models, priors, n_obs):
        
        self.path = path

        lc_file = open(path)
        self.lc = json.load(lc_file)
        lc_file.close()

        self.init_time = 0 # first element of first element of json file (Tyler: analysis - get_trigger_time function)

        self.label = os.path.basename(path).split('.')[0]   #check
        self.models = models
        self.priors = priors
        self.mask = np.zeros(n_obs) 

    def get_priors(self, model):

        model_prior = os.path.join(self.priors, f'{model}.prior')

    def compute_models(self, outdir):

        for model in self.models:

            model_prior = self.get_priors(model)

            # compute lightcurve models for each prior

            #### idx_results_path, idx_bestfit_paths = timestep_lightcurve_analysis(self.lc, model, model_prior, outdir, )

    def mask_lightcurve(self):
        '''
        Masks the true lightcurve so only the observed time-points have values.

        Assumptions: 
        - len(mask) == max len(lc). Since len(mask) = max(time), this should be true

        Args:
        - mask (dict): dictionary holding the timepoints where the object was observed (1) or not observed (0) {'ztfg': [1 1 0 1]}
        - lc (json): the true observations for the object in json format
        - model_n: name of the lightcurve model

        Returns:
        - masked file name: 'lc_masked_{model_n}.json'
        '''

        for k in self.lc.keys():
            del_count = 0

            for i in range(len(self.lc[k])):
                if self.mask[k][i] == 0:
                    del self.lc[k][i - del_count]
                    del_count += 1

        masked_file_name = f"lc_masked_{self.label}.json"
        masked_file = open(masked_file_name, "w")
        json.dump(self.lc, masked_file, indent = 6)
        masked_file.close()

        return masked_file_name

    def get_masked_lc(self, idx):   # what do we need to return here?
        
        # update mask at new timepoint
        self.mask[idx] = 1

        # mask lightcurve and return ____
        return self.mask_lightcurve()
        





