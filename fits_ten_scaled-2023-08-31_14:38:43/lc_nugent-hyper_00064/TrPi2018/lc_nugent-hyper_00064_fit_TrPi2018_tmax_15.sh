#!/bin/bash
#SBATCH --job-name=lc_nugent-hyper_00064_fit_TrPi2018_tmax_15
#SBATCH --time=23:59:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8gb
#SBATCH -o fits_ten_scaled-2023-08-31_14:38:43/lc_nugent-hyper_00064/TrPi2018/%x_%j.out
#SBATCH -e fits_ten_scaled-2023-08-31_14:38:43/lc_nugent-hyper_00064/TrPi2018/%x_%j.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=ztfrest@gmail.com
cd ~/dsmma_kn_23
source /home/cough052/barna314/anaconda3/bin/activate nmma_canary
light_curve_analysis --data injections_ten_scaled/lc_nugent-hyper_00064.json --model TrPi2018 --label lc_nugent-hyper_00064_fit_TrPi2018_tmax_15 --prior ./priors/TrPi2018.prior --svd-path svdmodels --filters ztfg --tmin 0.1 --tmax 15.099999999999996 --dt 0.5 --trigger-time 0.1 --error-budget 1 --nlive 1024 --remove-nondetections --ztf-uncertainties --ztf-ToO 180 --outdir fits_ten_scaled-2023-08-31_14:38:43/lc_nugent-hyper_00064/TrPi2018 --plot --bestfit  --detection-limit "{'r':21.5, 'g':21.5, 'i':21.5}"