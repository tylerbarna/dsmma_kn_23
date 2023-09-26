'''
functions for generating injections. Assumes nmma is at least updated to version 0.11.1, which added zenodo support as well as corrections to several previous issues relating to injection generation behaviour (naming and inclusion of simulation_id).
'''
import bilby.core
import json
import numpy as np
import os 

from argparse import Namespace 

from nmma.eos import create_injection

def generate_injection(model, outDir, injection_label=None,prior=None,):
    '''
    Generates injection for a given model
    
    Args:
    - model (str): model to generate injections for
    - outDir (str): output directory for injections
    - injection_label (str): identifying label for injection (default=None)
    - prior (str): path to prior file (default=None). If None, will look for prior in ./priors/ directory with name <model>.prior
    
    Returns:
    - injection_path (str): path to injection file
    '''
    if prior is None:
        prior = os.path.join('./priors/',model+'.prior')
    assert os.path.exists(prior), 'prior file {} does not exist'.format(prior)
    
    injection_path = os.path.join(outDir, 'inj_'+model+'_'+injection_label+'.json')
    
    args = Namespace( ## based on Michael's implementation in nmma unit test
        prior_file=prior,
        injection_file=None,
        reference_frequency=20,
        aligned_spin=False,
        filename=injection_path,
        extension="json",
        n_injection=1,
        trigger_time=0,
        gps_file=None,
        deltaT=0.2,
        post_trigger_duration=2,
        duration=4,
        generation_seed=42,
        grb_resolution=5,
        eos_file='../nmma/example_files/eos/ALF2.dat', ## assumes nmma is in same root directory as this repo
        binary_type="BNS",
        eject=False,
        detections_file=None,
        indices_file=None,
        original_parameters=True,
	repeated_simulations=0,
        )
    create_injection.main(args)
    assert os.path.exists(injection_path), 'injection file {} was not created'.format(injection_path)
    
    return injection_path

def get_parameters(injection_file, injection_index=0):
    '''
    read the parameters from the injection file and return them as a dictionary
    
    Args:
    - injection_file (str): path to injection file
    - injection_index (int, array): index of injection to read (default=0)
    
    Returns:
    - parameters (dict): dictionary of parameters
    Note: this function assumes by default that the injection file contains a single injection. To read multiple injections in a single dictionary, pass the injection_index as a list of integers, e.g. injection_index=[0,1,2]
    '''
    with open(injection_file,'r') as f:
        injection = json.load(f, object_hook=bilby.core.utils.decode_bilby_json)
    injection_content = injection['injections']
    
    for key, value in injection_content.items(): ## handles conversion to numpy arrays so injection_index can be a list/array of indices
        if isinstance(value, list):
            injection_content[key] = np.array(value)
    
    parameters = {
        key: value[injection_index] for key, value in injection_content.items()
    }
    
    return parameters
    
    

    
