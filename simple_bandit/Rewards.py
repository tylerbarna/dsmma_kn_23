###################################################################################################
###################################################################################################
# imports
###################################################################################################
import numpy as np

###################################################################################################
###################################################################################################
# contains reward functions
###################################################################################################

def stochastic_reward(dat, model_of_interest, stat):
    '''
    Calculates the reward R = L_k - L_j 
    (L_k be the stat of the model of interest, L_j the greatest stat out of all the stat except the model of interest)

    Args:
    - dat(dict): dictionary with statistics for each model
    - example dict: {modelA : {"log_bayes": float, 
                             "likelihood": float},
                   modelB : {"log_bayes": float, 
                              "likelihood": float}
                  }
    - model_of_interest (str)
    - stat (str): which statistic to use: 'log_bayes' or 'likelihood'   # TODO: make sure you can only choose an available stat
    '''
    all_stats = []
    model_of_interst_stat = None

    for key in dat:

        if key == model_of_interest:
            model_of_interst_stat = dat[key][stat]
        else:
            all_stats.append(dat[key][stat])

    R = model_of_interst_stat - max(all_stats)

    return R
