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

        self.n_obs = np.zeros(self.n_obj)
        self.obj_rewards = np.zeros(self.n_obj)
        self.avg_rewards = np.zeros(self.n_obj)
    
        self.cur_obj = None
        self.t = 0

    def initial_reward(self, obj_idx, reward):
        
        self.obj_rewards[obj_idx] += reward     # should be empty, but doing += to be safe
        self.avg_rewards[obj_idx] += reward     # technically no observations, so cannot use 'update_reward' function

    ''' 
    Play each arm once, then in round t > n, 
    select arm with highest avg reward plus some confidence interval

    All rewards start at infinity if the arm hasn't been pulled so the 
    algorithm should pull all arms at least once
    '''
    def choose_obj(self):

        if self.t <= (self.n_obj - 1):  # can delete this if statement since we always have some initial observations
            obj = self.t
        else:
            obj_ucbs = np.zeros(self.n_obj)

            for i in range(self.n_obj):

                confidence_interval = np.sqrt(np.divide(2 * np.log(self.t), self.n_obs[i]))

                obj_ucbs[i] = self.avg_rewards[i] + confidence_interval

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
