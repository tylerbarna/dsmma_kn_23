#!/bin/bash
#SBATCH --job-name=lc_nugent-hyper_00003_fit_TrPi2018_tmax_13
#SBATCH --time=23:59:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8gb
#SBATCH -o lightcurve_fits/lc_nugent-hyper_00003/TrPi2018/%x_%j.out
#SBATCH -e lightcurve_fits/lc_nugent-hyper_00003/TrPi2018/%x_%j.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=ztfrest@gmail.com
cd ~/dsmma_kn_23
source /home/cough052/barna314/anaconda3/bin/activate nmma_canary
light_curve_analysis --data lightcurve_sample/lc_nugent-hyper_00003.json --model TrPi2018 --label lc_nugent-hyper_00003_fit_TrPi2018_tmax_13 --prior ./priors/TrPi2018.prior --svd-path ~/dsmma_kn_23/svdmodels --filters ztfg --tmin 0.1 --tmax 13.099999999999998 --dt 0.5 --trigger-time 0.1 --error-budget 1 --nlive 1024 --remove-nondetections --ztf-uncertainties --ztf-ToO 180 --outdir lightcurve_fits/lc_nugent-hyper_00003/TrPi2018 --plot --bestfit  --detection-limit "{'r':21.5, 'g':21.5, 'i':21.5}" --remove-nondetections