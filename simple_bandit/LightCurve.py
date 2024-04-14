###################################################################################################
###################################################################################################
# imports
###################################################################################################
import numpy as np
import os
import json

import sys  #############################################################

sys.path.append(
    "~/dsmma_kn_23"
)  #############################################################

# from simple_bandit.Models import Models
from Models import Models


###################################################################################################
###################################################################################################
# Class: LightCurve - saves observations of one object
#                   - for simulations, it grabs the "observed" points from a given lightcurve
#                   - keeps track of the intervals that the object was observed
#                   - keeps a dictionary of the fit statistics for each time the lc was observed
###################################################################################################
class LightCurve:
    """
    LightCurve object keeps lightcurve file path name, fit statistics, and keeps track of intervals observed

    Args:
    - path (str): (For SIMULATED data) file path containing all the observations of a simulated lightcurve
                : (For ONLINE data) file that contains observations of lightcurve, and is the file where new obs are stored
    - n_intervals (int): number of intervals the bandit will run
    -  sim (Boolean): True if this is simulated data, false otherwise

    Notes:
    - filter is currently hard-coded as 'ztfg'
    """

    def __init__(self, path, n_intervals, sim, all_models):

        self.path = path
        self.label = os.path.basename(self.path).split(".")[0]  # CHECK
        self.outdir = os.path.dirname(self.path)
        self.intervals_obs = np.zeros(
            n_intervals + 1
        )  # add one because all lightcurves have initial observations saved in the zero-th place
        self.s = sim

        self.all_models = all_models

        if self.s == True:
            # read in true LC
            true_lc_file = open(self.path)
            self.true_lc = json.load(true_lc_file)
            true_lc_file.close()

            # make empty lc dict
            self.observed_lc = {"ztfg": [self.true_lc["ztfg"][0]]}  # CHECK

            # create file path name
            self.observed_lc_path = os.path.join(
                self.outdir, "observed_" + self.label + ".json"
            )

        else:
            # just need path of lc object observations
            self.observed_lc_path = self.path

        self.fit_stats = {}  # CHECK : empty dictionary

    def update_intervals_obs(self, idx):
        """update the array that keeps a 1 if the lc was observed at that interval, 0 else"""
        self.intervals_obs[idx] = 1

    def update_lc(self, start_int, end_int):
        """for simulated data: adds new observations to observed_lc_path that happened within (start_int, end_int)"""

        # get new obs from true lc
        lc_arr = np.asarray(self.true_lc["ztfg"])
        time_cutoff = lc_arr[(lc_arr[:, 0] >= start_int) & (lc_arr[:, 0] <= end_int)]
        # print(start_int, end_int) #####################################################################
        time_cutoff_list = np.ndarray.tolist(time_cutoff)
        # print(time_cutoff_list[0]) #####################################################################
        # print(self.observed_lc['ztfg']) #####################################################################

        # add new obs to observed_lc
        print("DEBUG PRINTS")
        print(self.observed_lc["ztfg"])
        print(time_cutoff_list)
        ## only do if there are new observations
        if len(time_cutoff_list) > 0:
            self.observed_lc["ztfg"] = np.ndarray.tolist(
                np.append(self.observed_lc["ztfg"], time_cutoff_list, axis=0)
            )

        # rewrite json file with new observed_lc
        f = open(self.observed_lc_path, "w")
        json.dump(self.observed_lc, f, indent=6)
        f.close()

    def get_model_outputs(self, idx):
        """call run_models and get model outputs (likelihood, bayes factor) and save in fit_stats dict with idx as key"""
        # call run models if there's more data
        # print('running models for lightcurve ' + self.label + ' at interval ' + str(idx) + '...')
        out = self.all_models.run_models(self.observed_lc_path, self.outdir)

        idx_str = str(idx)

        self.fit_stats[idx_str] = out

    def model_fits(self, idx):
        idx_str = str(idx)
        return self.fit_stats[idx_str]

    def observe_lightcurve(self, idx, start_int=None, end_int=None):
        """
        after lc object has gotten new observations (for simulated data: add obs within given time), run model fits, and save output to fit_stats dict

        Args:
        - idx (int): index of the observation interval of the bandit (should have a one added to it because initial obs of LightCurve object are in 0-th place)
        - start_int (float): start time of observation interval, don't need for online data (default=None)
        - end_int (float): end time of observation interval, don't need for online data (default=None)

        Returns:
        - dictionary of model fits
        """
        self.update_intervals_obs(idx)

        if self.s == True:
            self.update_lc(start_int, end_int)

        self.get_model_outputs(
            idx
        )  ## maybe add print statement like: I am about to start running models

        return self.model_fits(idx)
