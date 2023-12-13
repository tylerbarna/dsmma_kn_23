import os
import subprocess
import json

def create_lightcurve_samples(output='injections/parameter_test', multiplier=100, rewrite=False):
    if rewrite:
        os.system(f'rm -rf {output}')
    os.makedirs(output, exist_ok=True), os.makedirs(os.path.join(output, 'validated'), exist_ok=True), os.makedirs(os.path.join(output, 'unvalidated'), exist_ok=True)
    subprocess.run('conda activate nmma_dev', shell=True)
    validate_str = ['python3',
                    'generation_script.py',
                    '--models', 'Bu2019lm', 'TrPi2018', 'Piro2021', 'nugent-hyper',
                    '--outdir', os.path.join(output, 'validated'),
                    '--min-detections', '3',
                    '--min-detections-cutoff', '5',
                    '--multiplier', str(multiplier),
                    '--ztf-sampling',
                    '--parallel'
                    ]
    unvalidate_str = ['python3',
                    'generation_script.py',
                    '--models', 'Bu2019lm', 'TrPi2018', 'Piro2021', 'nugent-hyper',
                    '--outdir', os.path.join(output, 'unvalidated'),
                    '--min-detections', '3',
                    '--min-detections-cutoff', '5',
                    '--multiplier', str(multiplier),
                    '--ztf-sampling',
                    '--parallel',
                    '--no-validate'
                    ]
    # subprocess.run(' '.join(validate_str), shell=True)
    subprocess.run(' '.join(unvalidate_str), shell=True)
    
    return os.path.join(output, 'validated'), os.path.join(output, 'unvalidated')

def main():
    create_lightcurve_samples(output='injections/parameter_test', multiplier=666, rewrite=True)
    
if __name__ == '__main__':
    main()