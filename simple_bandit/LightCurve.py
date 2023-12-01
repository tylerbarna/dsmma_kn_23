###################################################################################################
###################################################################################################
# imports
###################################################################################################
import numpy as np
import os
import json
from Models import run_models
###################################################################################################
###################################################################################################
# Class: LightCurve - saves observations of one object
#                   - for simulations, it can caluclate the observed points from a given lightcurve
#                   - keeps track of the intervals that the object was observed (extra check)
#                   - keeps a dictionary of the fit statistics for each time the lc was observed
###################################################################################################
class LightCurve:

    def __init__(self, path, n_intervals):

        self.path = path

        lc_file = open(path)
        self.lc = json.load(lc_file)
        lc_file.close()

        self.label = os.path.basename(self.path).split('.')[0]   # CHECK
        
        self.intervals_obs = np.zeros(n_intervals) 

        self.fit_stats = {} # CHECK : empty dictionary

        ###########################################################
        ### Add the model fits for the initial observations here
        ### Simulation var == TRUE

        ''' Simulations case:'''
        self.observed_lc = {'ztfg: []'} # CHECK : empty dictionary to add observations

        ''' Online case: observed lightcurve is just the lightcurve given'''
        # self.observed_lc = self.lc

    def update_intervals_obs(self, idx):
        
        # update the array that keeps a 1 if the lc was observed at that interval, 0 else
        self.intervals_obs[idx] = 1

    def get_new_obs(self, start_int, end_int):
        pass
        ''' Simulations case:'''
        # given start and end time of interval observed, get observations to add to observed_lc from lc

    def get_model_outputs(self, idx):
        pass
        # get model outputs and save in fit_stats dict with idx as key
        run_models(self.observed_lc)

    def return_model_outputs(self, idx):

        return self.fit_stats[idx]

    def observe_lightcurve(self, idx, start_int, end_int):
        pass
        # given start and end time of interval observed, update intervals_obs for this object, 
        # get new observations and add to observed_lc
        # and get model outputs (call models script)

        self.update_intervals_obs(idx)
        self.get_new_obs(start_int, end_int)    # Simulations case
        self.get_model_outputs(idx)
        
        return self.fit_stats[idx]


###################################################################################################
# graveyard
###################################################################################################
    # def mask_lightcurve(self):
    #     '''
    #     Masks the true lightcurve so only the observed time-points have values.

    #     Assumptions: 
    #     - len(mask) == max len(lc). Since len(mask) = max(time), this should be true

    #     Args:
    #     - mask (dict): dictionary holding the timepoints where the object was observed (1) or not observed (0) {'ztfg': [1 1 0 1]}
    #     - lc (json): the true observations for the object in json format
    #     - model_n: name of the lightcurve model

    #     Returns:
    #     - masked file name: 'lc_masked_{model_n}.json'
    #     '''

    #     for k in self.lc.keys():
    #         del_count = 0

    #         for i in range(len(self.lc[k])):
    #             if self.mask[k][i] == 0:
    #                 del self.lc[k][i - del_count]
    #                 del_count += 1

    #     masked_file_name = f"lc_masked_{self.label}.json"
    #     masked_file = open(masked_file_name, "w")
    #     json.dump(self.lc, masked_file, indent = 6)
    #     masked_file.close()

    #     return masked_file_name

    # def calc_time_from_obs_idx(self, t):
    #     '''
    #     Calculate the 
    #     '''

    # def get_masked_lc(self, idx, time):   # what do we need to return here?
        
    #     # update mask at new observation index
    #     self.mask[idx] = 1

    #     # mask lightcurve and return the file name of new masked lightcurve
    #     return self.mask_lightcurve()
    

        





