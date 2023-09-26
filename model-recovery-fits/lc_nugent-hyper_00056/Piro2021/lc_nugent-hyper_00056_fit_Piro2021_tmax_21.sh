#!/bin/bash
#SBATCH --partition=shared
#SBATCH --account=umn131
#SBATCH --job-name=lc_nugent-hyper_00056_fit_Piro2021_tmax_21
#SBATCH --time=23:59:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8gb
#SBATCH -o model-recovery-fits/lc_nugent-hyper_00056/Piro2021/%x_%j.out
#SBATCH -e model-recovery-fits/lc_nugent-hyper_00056/Piro2021/%x_%j.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=ztfrest@gmail.com
cd ~/dsmma_kn_23
source activate nmma_env
light_curve_analysis --data model-recovery-injections/lc_nugent-hyper_00056.json --model Piro2021 --label lc_nugent-hyper_00056_fit_Piro2021_tmax_21 --prior ./priors/Piro2021.prior --svd-path ~/dsmma_kn_23/svdmodels --filters ztfg --tmin 0.1 --tmax 21 --dt 0.5 --trigger-time 44244.24122095766 --error-budget 1 --nlive 1024 --ztf-uncertainties --ztf-ToO 180 --outdir model-recovery-fits/lc_nugent-hyper_00056/Piro2021 --plot --bestfit  --detection-limit "{'r':21.5, 'g':21.5, 'i':21.5}" --remove-nondetections --verbose