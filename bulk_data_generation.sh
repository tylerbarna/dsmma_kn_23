#!/bin/bash
#SBATCH --name=bulk_data_generation
#SBATCH --time=71:59:59
#SBATCH --mail-type=ALL
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=8gb
#NOTSBATCH -p amdsmall
#SBATCH -o ./logs/%x_%j.out
#SBATCH -e ./logs/%x_%j.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=ztfrest@gmail.com

scratch_dir="/scratch.global/barna314/bulk_data_generation"
injection_scratch = "/scratch.global/barna314/injection_data"
fits_scratch = "/scratch.global/barna314/fits_data"
fit_results = "/home/cough052/barna314/dsmma_kn_23/fit_results"
mkdir -p ${scratch_dir}
mkdir -p ${injection_scratch}
mkdir -p ${fits_scratch}
mkdir -p ${fit_results}

source /home/cough052/barna314/anaconda3/bin/activate nmma38

python3 /home/cough052/barna314/dsmma_kn_23/lightcurve_script.py --outdir ${injection_scratch} --multiplier $1

wait # wait for all background processes to finish before proceeding

python3 /home/cough052/barna314/dsmma_kn_23/analysis_script.py --outdir ${fits_scratch}

wait 

python3 /home/cough052/barna314/dsmma_kn_23/calc_residuals.py --data ${fits_scratch} --outdir ${fit_results}
