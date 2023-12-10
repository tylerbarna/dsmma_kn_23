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
#                   - for simulations, it grabs the "observed" points from a given lightcurve
#                   - keeps track of the intervals that the object was observed
#                   - keeps a dictionary of the fit statistics for each time the lc was observed
###################################################################################################
class LightCurve:
    ''' 
    LightCurve object keeps lightcurve file path name, fit statistics, and keeps track of intervals observed

    Args: 
    - path (str): (For SIMULATED data) file path containing all the observations of a simulated lightcurve
                : (For ONLINE data) file that contains observations of lightcurve, and is the file where new obs are stored
    - n_intervals (int): number of intervals the bandit will run
    -  sim (Boolean): True if this is simulated data, false otherwise

    Notes:
    - filter is currently hard-coded as 'ztfg'
    '''
    def __init__(self, path, n_intervals, sim):

        self.path = path
        self.label = os.path.basename(self.path).split('.')[0]   # CHECK
        self.outdir = os.path.dirname(self.path)
        self.intervals_obs = np.zeros(n_intervals)
        self.s = sim

        if self.s == True:
            # read in true LC
            true_lc_file = open(self.path)
            self.true_lc = json.load(true_lc_file)
            true_lc_file.close()

            # make empty lc dict
            self.observed_lc = {'ztfg' : None} # CHECK : empty dictionary to add observations works

            # create file path name
            self.observed_lc_path = os.path.join(self.outdir, 'observed_lc_'+self.label+'.json')
        
        else:
            # just need path of lc object observations
            self.observed_lc_path = self.path

        self.fit_stats = {} # CHECK : empty dictionary

    def update_intervals_obs(self, idx):
        '''update the array that keeps a 1 if the lc was observed at that interval, 0 else'''
        self.intervals_obs[idx] = 1

    def update_lc(self, start_int, end_int):
        '''for simulated data: adds new observations to observed_lc_path that happened within (start_int, end_int)'''
        
        # get new obs from true lc
        lc_arr = np.asarray(self.true_lc['ztfg'])
        time_cutoff = lc_arr[(lc_arr[:,0]  >= start_int) & (lc_arr[:,0] <= end_int)]
        time_cutoff_list = np.ndarray.tolist(time_cutoff)

        # add new obs to observed_lc
        self.observed_lc['ztfg'] = np.ndarray.tolist(np.append(self.observed_lc['ztfg'], time_cutoff_list, axis = 0))

        # rewrite json file with new observed_lc
        f = open(self.observed_lc_path, "w")
        json.dump(self.observed_lc, f, indent = 6)
        f.close()

    def get_model_outputs(self, idx):
        '''call run_models and get model outputs (likelihood, bayes factor) and save in fit_stats dict with idx as key'''
        out = run_models(self.observed_lc_path, self.outdir)

        idx_str = str(idx)

        self.fit_stats[idx_str] = out

    def model_fits(self, idx):

        return self.fit_stats[idx]

    def observe_lightcurve(self, idx, start_int, end_int):
        ''' after lc object has gotten new observations (for simulated data: add obs within given time), run model fits, and save output to fit_stats dict'''
        self.update_intervals_obs(idx)

        if self.s == True:
            self.update_lc(start_int, end_int)

        self.get_model_outputs(idx) ## maybe add print statement like: I am about to start running models
        
        return self.model_fits(idx)


###################################################################################################
# graveyard
###################################################################################################

    # def get_new_obs(self, start_int, end_int):

    #     if self.s == True:
    #         pass
    #         # given start and end time of interval observed, get observations to add to observed_lc from lc
    #         masked_file = open(self.observed_lc_path, "w")
    #         json.dump(self.observed_lc, masked_file, indent = 6)
    #         masked_file.close()
    #     else:
    #         # re-load in the lc file from path to account for new observations
    #         new_lc_file = open(self.path)   ### assuming new observations will be added to the same file path
    #         new_lc = json.load(new_lc_file)
    #         new_lc_file.close()

    #         self.observed_lc = new_lc

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
    

        





