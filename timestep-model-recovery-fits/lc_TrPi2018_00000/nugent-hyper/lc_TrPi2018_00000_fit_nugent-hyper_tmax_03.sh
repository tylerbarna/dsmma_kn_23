#!/bin/bash
#SBATCH --partition=shared
#SBATCH --account=umn131
#SBATCH --job-name=lc_TrPi2018_00000_fit_nugent-hyper_tmax_03
#SBATCH --time=23:59:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8gb
#SBATCH -o timestep-model-recovery-fits/lc_TrPi2018_00000/nugent-hyper/%x_%j.out
#SBATCH -e timestep-model-recovery-fits/lc_TrPi2018_00000/nugent-hyper/%x_%j.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=ztfrest@gmail.com
cd /expanse/lustre/projects/umn131/tbarna/
source activate nmma_dev
lightcurve-analysis --data /home/tbarna/dsmma_kn_23/characteristic_injections/lc_TrPi2018_00000.json --model nugent-hyper --label lc_TrPi2018_00000_fit_nugent-hyper_tmax_03 --prior /home/tbarna/dsmma_kn_23./priors/nugent-hyper.prior --svd-path ~/dsmma_kn_23/svdmodels --filters ztfg --tmin 0.1 --tmax 3.1 --dt 0.5 --trigger-time 44245.005606767096 --error-budget 1 --nlive 1024 --ztf-uncertainties --ztf-ToO 180 --outdir timestep-model-recovery-fits/lc_TrPi2018_00000/nugent-hyper --bestfit  --detection-limit "{'r':21.5, 'g':21.5, 'i':21.5}" --remove-nondetections --verbose