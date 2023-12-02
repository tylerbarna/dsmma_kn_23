###################################################################################################
###################################################################################################
# imports
###################################################################################################
import numpy as np

###################################################################################################
###################################################################################################
# Rewards - has the reward functions
###################################################################################################

def stochastic_reward(dat):
    pass
    # given dat dict with BF/residual/likelihood for a lightcurve, calculate the reward:
    # R = L_k - max(L_j) (where L_k is the kilonova model likelihood, L_j is the greatest L of 
    # a model that is not the kilonova model)
    # assume the kilonova model is always the first one in the list

    k_model_stat = dat['bf'][0]     # CHECK you are using the bayes factor, make sure you make dict key as expected
    
    other_models_stats = dat['bf'][1:]

    R = k_model_stat - max(other_models_stats)

    return R
