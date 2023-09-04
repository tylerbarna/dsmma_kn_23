#!/bin/bash
#SBATCH --job-name=lc_TrPi2018_00002_fit_nugent-hyper_tmax_05
#SBATCH --time=23:59:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8gb
#SBATCH -o fits_ten_scaled-2023-08-31_14:38:43/lc_TrPi2018_00002/nugent-hyper/%x_%j.out
#SBATCH -e fits_ten_scaled-2023-08-31_14:38:43/lc_TrPi2018_00002/nugent-hyper/%x_%j.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=ztfrest@gmail.com
cd ~/dsmma_kn_23
source /home/cough052/barna314/anaconda3/bin/activate nmma_canary
light_curve_analysis --data injections_ten_scaled/lc_TrPi2018_00002.json --model nugent-hyper --label lc_TrPi2018_00002_fit_nugent-hyper_tmax_05 --prior ./priors/nugent-hyper.prior --svd-path svdmodels --filters ztfg --tmin 0.1 --tmax 5.1 --dt 0.5 --trigger-time 0.1 --error-budget 1 --nlive 1024 --remove-nondetections --ztf-uncertainties --ztf-ToO 180 --outdir fits_ten_scaled-2023-08-31_14:38:43/lc_TrPi2018_00002/nugent-hyper --plot --bestfit  --detection-limit "{'r':21.5, 'g':21.5, 'i':21.5}"