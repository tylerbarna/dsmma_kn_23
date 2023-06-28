'''
functions for generating injections. Assumes nmma is at least updated to version 0.11.1, which added zenodo support as well as corrections to several previous issues relating to injection generation behaviour (naming and inclusion of simulation_id).
'''

import os 
from argparse import Namespace 


from nmma.eos import create_injection

def generate_injections(model, outDir, injection_label=None,prior=None,):
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
    
    injection_path = os.path.join(outDir, 'injection_'+model+'_'+injection_label+'.json')
    
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
        )
    create_injection.main(args)
    assert os.path.exists(injection_path), 'injection file {} was not created'.format(injection_path)
    
    return injection_path

    