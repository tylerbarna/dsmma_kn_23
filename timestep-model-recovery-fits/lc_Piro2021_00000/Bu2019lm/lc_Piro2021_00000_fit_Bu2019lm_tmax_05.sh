#!/bin/bash
#SBATCH --partition=shared
#SBATCH --account=umn131
#SBATCH --job-name=lc_Piro2021_00000_fit_Bu2019lm_tmax_05
#SBATCH --time=23:59:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8gb
#SBATCH -o timestep-model-recovery-fits/lc_Piro2021_00000/Bu2019lm/%x_%j.out
#SBATCH -e timestep-model-recovery-fits/lc_Piro2021_00000/Bu2019lm/%x_%j.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=ztfrest@gmail.com
cd /expanse/lustre/projects/umn131/tbarna/
source activate nmma_dev
lightcurve-analysis --data /home/tbarna/dsmma_kn_23/characteristic_injections/lc_Piro2021_00000.json --model Bu2019lm --label lc_Piro2021_00000_fit_Bu2019lm_tmax_05 --prior /home/tbarna/dsmma_kn_23./priors/Bu2019lm.prior --svd-path ~/dsmma_kn_23/svdmodels --filters ztfg --tmin 0.1 --tmax 5.1 --dt 0.5 --trigger-time 44243.702358906434 --error-budget 1 --nlive 1024 --ztf-uncertainties --ztf-ToO 180 --outdir timestep-model-recovery-fits/lc_Piro2021_00000/Bu2019lm --bestfit  --detection-limit "{'r':21.5, 'g':21.5, 'i':21.5}" --remove-nondetections --verbose