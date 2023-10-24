#!/bin/bash
#SBATCH --partition=shared
#SBATCH --account=umn131
#SBATCH --job-name=lc_Piro2021_00000_fit_Piro2021_tmax_04
#SBATCH --time=23:59:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8gb
#SBATCH -o timestep-model-recovery-fits/lc_Piro2021_00000/Piro2021/%x_%j.out
#SBATCH -e timestep-model-recovery-fits/lc_Piro2021_00000/Piro2021/%x_%j.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=ztfrest@gmail.com
cd /expanse/lustre/projects/umn131/tbarna/
source activate nmma_dev
lightcurve-analysis --data /home/tbarna/dsmma_kn_23/characteristic_injections/lc_Piro2021_00000.json --model Piro2021 --label lc_Piro2021_00000_fit_Piro2021_tmax_04 --prior /home/tbarna/dsmma_kn_23./priors/Piro2021.prior --svd-path ~/dsmma_kn_23/svdmodels --filters ztfg --tmin 0.1 --tmax 4.1 --dt 0.5 --trigger-time 44243.702358906434 --error-budget 1 --nlive 1024 --ztf-uncertainties --ztf-ToO 180 --outdir timestep-model-recovery-fits/lc_Piro2021_00000/Piro2021 --bestfit  --detection-limit "{'r':21.5, 'g':21.5, 'i':21.5}" --remove-nondetections --verbose