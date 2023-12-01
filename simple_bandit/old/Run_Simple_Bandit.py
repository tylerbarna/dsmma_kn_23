################################################################################################## 

'''

Run_Simple_Bandit.py

Description : Can be used to call Multi_Arm_Bandit function from Simple_Bandit.py to run a 
              multi-arm-bandit model.

              Currently uses 'statsDataFrame.csv' as the input data which has 3 models : 'Bu2019lm' 
                                                                                         'TrPi2018'
                                                                                         'nugent-hyper'

              Any set of objects in the data can be used as long as they fulfill the input 
              requirements. Currently, it uses objects : 'ZTF21abqraak'
                                                         'ZTF21aceqcwu'
                                                         'ZTF22aabvdtc'
                                                         'ZTF22aapgcak'
                                                         'ZTF22aawacjw'
              They each have at least 7 log bayes factor observations for each model, so the model
              is called with num_rounds = 7.

              You can change the inputs in the #### DEFINE INPUTS HERE ###### section of the code.

Author: Ana Uribe (uribe055@umn.edu)

'''

################################################################################################## 
################################    imports    ###################################################

import pandas as pd
from simple_bandit.old.Simple_Bandit import Multi_Arm_Bandit



################################################################################################## 

################################      Load and Process data       ################################

# read in data
raw_data = pd.read_csv('statsDataframe.csv')    # TODO : ask user for path file or make more general


# extract columns of interest
obj, start_day, stop_day, start_date, stop_date, model, log_bayes_factor = [], [], [], [], [], [], [] 

nan_bayes_f = raw_data['log_bayes_factor'].isnull()

for row, bf_is_null in zip(raw_data.values, nan_bayes_f):

    if not bf_is_null:

        obj.append(row[5])

        days = row[1].split('-')
        start_day.append(int(days[0]))
        stop_day.append(int(days[1]))

        start_date.append(row[2])
        stop_date.append(row[3])

        model.append(row[7])

        log_bayes_factor.append(float(row[16]))

# create dataframe
data = {'obj' :                 obj,
        'start_day' :           start_day,
        'stop_day':             stop_day,
        'start_date' :          start_date,
        'stop_date' :           stop_date,
        'model' :               model,
        'log_bayes_factor' :    log_bayes_factor}

df = pd.DataFrame(data)
  

################################################################################################## 

################################        Run Multi-Arm-Bandit      ################################

''' 
INPUTS for Multi-Arm Bandit are defined as follows : 

        (int)              num_rounds  - total number of rounds, must have at least this many observations per for
                                          each object
        (list)              obj         - list of strings corresponding to the names of the objects to use
        (list)              models      - list of strings corresponding to the names of the models to use
        (float)             delta       - hyperparameter that helps define Upper Confidence Bound. Defined as 
                                          1 / (num_rounds^2), must be \in (0, 1)
        (pandas DataFrame)  dataframe   - contains all observations. Columns: start_day, stop_day,
                                          start_date, stop_date, model, log_bayes_factor
'''


########### DEFINE INPUTS HERE ################

num_rounds = 7
object_names = ['ZTF21abqraak', 'ZTF21aceqcwu', 'ZTF22aabvdtc', 'ZTF22aapgcak', 'ZTF22aawacjw']
models = ['Bu2019lm', 'TrPi2018', 'nugent-hyper']
delta = 1 / (num_rounds ** 2)

###############################################

# call model
mab_model = Multi_Arm_Bandit(num_rounds, object_names, models, delta, df)

mab_model.run()
