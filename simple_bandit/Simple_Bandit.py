################################################################################################## 

'''

Simple_Bandit.py

Description : Contains a module can be called to run a simple multi-arm bandit model. The model
              implementation is based on Bandit Algorithms by Tor Lattimore and Csaba Szepersvári
              chapters 6 and 7.

Author: Ana Uribe (uribe055@umn.edu)

'''

################################################################################################## 
################################    imports    ###################################################

import numpy as np

################################################################################################## 
    
################################    Multi-Arm-Bandit CLASS    ####################################
''' 
INPUT : (int)               num_rounds  - total number of rounds, must have at least this many observations per for
                                          each object
        (list)              obj         - list of strings corresponding to the names of the objects to use
        (list)              models      - list of strings corresponding to the names of the models to use
        (float)             delta       - hyperparameter that helps define Upper Confidence Bound. Defined as 
                                          1 / (num_rounds^2)
        (pandas DataFrame)  dataframe   - contains all observations. Columns: start_day, stop_day,
                                          start_date, stop_date, model, log_bayes_factor
'''

class Multi_Arm_Bandit():

    def __init__(self, num_rounds, obj, models, delta, dataframe):

        self.n = num_rounds
        self.obj = obj
        self.models = models
        self.delta = delta
        self.df = dataframe

        self.k = len(obj)
        self.ucb = np.full((self.k,), np.nan)


    ################################################################################################## 

    ####################################    MAIN FUNCTION    ######################################### 
    '''     
    The multi-arm bandit model runs as follows:
    
    for t in (1, ... , n) rounds do
        Update upper confidence bounds
        Choose action A_t
        Observe reward X_t
    '''
    def run(self):

        trials = np.zeros(self.k)
        rewards = np.zeros(self.k)

        print(f'\nStarting Multi-arm Bandit... \nInitial trials: {trials}     rewards: {rewards}     UCB : {self.ucb}\n')

        for t in range(self.n):
            
            print(f'\nRound {t + 1} :')

            self.update_UCB(trials, rewards)
            print(f'UCB after update : {self.ucb}')

            idx = self.get_arm()

            print(f'Based on UCB, choose arm at index {idx}')

            A_t = self.obj[idx]

            trials[idx] += 1

            # get current object's t-th observations
            chosen_obs = []
            for i in range(len(self.models)):
                
                cur_model = self.models[i]

                # get log_bayes_factor (column 6 in df) for t-th observation of object A_t 
                # with specific model cur_model
                log_BF = self.df[self.df['obj'] == A_t].loc[self.df['model'] == cur_model].iloc[t][6]

                chosen_obs.append([cur_model, log_BF])

            cur_reward = self.get_X_t(chosen_obs)
            rewards[idx] += cur_reward
            
            print(f'trial count : {trials}      rewards: {rewards}')

        total_reward = np.sum(rewards)

        print('\nTotal reward for {} rounds: {:.4f}\n'.format(self.n, total_reward))

    
    ###################################################################################################
    
    ####################################   HELPER FUNCTIONS    ########################################
    ''' 
    The reward X_t for a certain round is calculated with the log bayes factor of the observation.
    The closer the value is to zero, the higher reward we want to give the model. 
    We define the reward function as : 
    log(x_m) - max_{i != m}[log(x_i)] for model of interest m and bayes factor x.
    INPUT : l_BF - (d, 2) array containing log_bayes_factors for the round: col 1 = model, col 2 = log_bayes_factor
            model_of_interest - string of the model we care about, default Bu2019lm

    OUTPUT : reward - float 
    '''
    def get_X_t(self, l_BF, model_of_interest = 'Bu2019lm'):

        max_log_x_i = None

        for row in l_BF:

            if row[0] == model_of_interest:
                
                log_x_m = row[1]      

            else:
                candidate_log_x_i = row[1]

                # keep track of max log(x_i)
                if max_log_x_i == None:
                    max_log_x_i = candidate_log_x_i
                elif candidate_log_x_i > max_log_x_i:
                    max_log_x_i = candidate_log_x_i
        
        reward = log_x_m - max_log_x_i

        return(reward)
    
    '''
    We must calculate the Upper Confidence Bound for all objects i to determine the action A to take (what object to observe).
    We calculate :
    UCB_i(t - 1, delta) = { \inf                                                         if T_i(t - 1) = 0
                          { \mu_hat_i(t - 1) + \sqrt( 2log(1/delta) / T_i(t - 1))        otherwise
    and update the global variable self.ucb

    INPUT : trails - (k,) array containing the number of times an arm has been chosen
          : rewards - (k,) array with the rewards from each arm
    '''
    def update_UCB(self, trials, rewards):

        for i in range(self.k):

            if trials[i] == 0:
                self.ucb[i] = np.inf
            else:
                self.ucb[i] = rewards[i] + np.sqrt( 2 * np.log(1 / self.delta) / trials[i])

    ''' 
    We choose action A_t = argmax(UCB_i(t - 1, delta)) where UCB_i is stored
    in self.ucb.
    
    OUTPUT : i - int index of chosen arm
    '''
    def get_arm(self):
        max_ucb = np.nanmax(self.ucb)

        for i in range(len(self.ucb)):
            if self.ucb[i] == max_ucb:
                return(i)