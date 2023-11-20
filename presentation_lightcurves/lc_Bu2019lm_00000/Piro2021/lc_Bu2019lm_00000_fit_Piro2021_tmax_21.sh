#!/bin/bash
#SBATCH --partition=shared
#SBATCH --account=umn131
#SBATCH --job-name=lc_Bu2019lm_00000_fit_Piro2021_tmax_21
#SBATCH --time=01:59:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8gb
#SBATCH -o presentation_lightcurves/lc_Bu2019lm_00000/Piro2021/%x_%j.out
#SBATCH -e presentation_lightcurves/lc_Bu2019lm_00000/Piro2021/%x_%j.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=ztfrest@gmail.com
cd /expanse/lustre/projects/umn131/tbarna/
source activate nmma_env
lightcurve-analysis --data /home/tbarna/dsmma_kn_23/presentation_lightcurves/lc_Bu2019lm_00000.json --model Piro2021 --label lc_Bu2019lm_00000_fit_Piro2021_tmax_21 --prior ~/dsmma_kn_23/priors/Piro2021.prior --svd-path ~/dsmma_kn_23/svdmodels --filters ztfg --tmin 0.1 --tmax 21.0 --dt 0.5 --trigger-time 44242.038981343736 --error-budget 1 --nlive 1024 --ztf-uncertainties --ztf-ToO 180 --outdir presentation_lightcurves/lc_Bu2019lm_00000/Piro2021 --bestfit  --detection-limit "{'r':21.5, 'g':21.5, 'i':21.5}" --remove-nondetections --plot