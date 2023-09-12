#!/bin/bash
#SBATCH --job-name=lc_nugent-hyper_00065_fit_nugent-hyper_tmax_11
#SBATCH --time=23:59:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8gb
#SBATCH -o fits_ten_scaled/lc_nugent-hyper_00065/nugent-hyper/%x_%j.out
#SBATCH -e fits_ten_scaled/lc_nugent-hyper_00065/nugent-hyper/%x_%j.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=ztfrest@gmail.com
cd ~/dsmma_kn_23
source /home/cough052/barna314/anaconda3/bin/activate nmma_canary
light_curve_analysis --data injections_ten_scaled/lc_nugent-hyper_00065.json --model nugent-hyper --label lc_nugent-hyper_00065_fit_nugent-hyper_tmax_11 --prior ./priors/nugent-hyper.prior --svd-path svdmodels --filters ztfg --tmin 0.1 --tmax 11.099999999999998 --dt 0.5 --trigger-time 0.1 --error-budget 1 --nlive 1024 --remove-nondetections --ztf-uncertainties --ztf-ToO 180 --outdir fits_ten_scaled/lc_nugent-hyper_00065/nugent-hyper --plot --bestfit  --detection-limit "{'r':21.5, 'g':21.5, 'i':21.5}"