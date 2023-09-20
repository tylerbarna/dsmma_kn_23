#!/bin/bash
#SBATCH --job-name=lc_TrPi2018_00000_fit_TrPi2018_tmax_19
#SBATCH --time=23:59:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8gb
#SBATCH -o fits_msi/lc_TrPi2018_00000/TrPi2018/%x_%j.out
#SBATCH -e fits_msi/lc_TrPi2018_00000/TrPi2018/%x_%j.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=ztfrest@gmail.com
cd ~/dsmma_kn_23
source /home/cough052/barna314/anaconda3/bin/activate nmma_env
light_curve_analysis --data injections/lc_TrPi2018_00000.json --model TrPi2018 --label lc_TrPi2018_00000_fit_TrPi2018_tmax_19 --prior ./priors/TrPi2018.prior --svd-path ~/dsmma_kn_23/svdmodels --filters ztfg --tmin 0.1 --tmax 19.099999999999998 --dt 0.5 --trigger-time 44244.01021906841 --error-budget 1 --nlive 1024 --ztf-uncertainties --ztf-ToO 180 --outdir fits_msi/lc_TrPi2018_00000/TrPi2018 --plot --bestfit  --detection-limit "{'r':21.5, 'g':21.5, 'i':21.5}" --remove-nondetections --verbose