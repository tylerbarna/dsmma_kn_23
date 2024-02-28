###################################################################################################
###################################################################################################
# imports
###################################################################################################
import numpy as np

###################################################################################################
###################################################################################################
# Class: UCB - Upper confidence bound multi-arm bandit
###################################################################################################
class UCB:
        
    def __init__(self, num_obj):
        
        self.n_obj = num_obj

        self.n_obs = np.zeros(self.n_obj) + 3 ## each object is observed at least 3 times prior to the bandit starting
        self.obj_rewards = np.zeros(self.n_obj)
        self.avg_rewards = np.zeros(self.n_obj)
    
        self.cur_obj = None
        self.t = 0

    def initial_reward(self, obj_idx, reward):
        '''
        Stores the inital rewards of each candidate object at the zero-th observation.
        Cannot use 'update_reward' function because this inital reward does not count as an observation.
        Changes the n_obs to ones so when the average reward is calculcated again, you divide by the right
        number of observations (instead of dividing the sum of two rewards by one).
        '''
        self.obj_rewards[obj_idx] += reward
        self.avg_rewards[obj_idx] += reward

        #self.n_obs[obj_idx] += 1 ## not actually adding an observation


    ''' 
    Play each arm once, then in round t > n, 
    select arm with highest avg reward plus some confidence interval

    All rewards start at infinity if the arm hasn't been pulled so the 
    algorithm should pull all arms at least once
    '''
    def choose_obj(self):
        
        # check that all objects have at least one observation, and observe the first object that doesn't
        # Do not need this if you are sure all objects will have initial obs
        # if np.argwhere(self.n_obs == 0).any():
        #     obj = (np.argwhere(self.n_obs == 0)[0][0])

        # else:
        obj_ucbs = np.zeros(self.n_obj)

        for i in range(self.n_obj):

            confidence_interval = np.sqrt(np.divide(2 * np.log(self.t), self.n_obs[i])) #if self.n_obs[i] != 0 else np.inf

            obj_ucbs[i] = self.avg_rewards[i] + confidence_interval

        print('current upper confidence bound array: ',obj_ucbs)
        obj = np.argmax(obj_ucbs)

        self.n_obs[obj] += 1

        self.cur_obj = obj

        self.t += 1

        return(obj)

    def update_model(self, reward):

        self.obj_rewards[self.cur_obj] += reward

        # calculate average reward
        for i in range(self.n_obj):
            if self.n_obs[i] != 0:
                self.avg_rewards[i] = self.obj_rewards[i] / self.n_obs[i]
