#!/bin/bash
#SBATCH --job-name=lc_Me2017_00000_fit_nugent-hyper_tmax_09
#SBATCH --time=23:59:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8gb
#SBATCH -o fits_msi/lc_Me2017_00000/nugent-hyper/%x_%j.out
#SBATCH -e fits_msi/lc_Me2017_00000/nugent-hyper/%x_%j.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=ztfrest@gmail.com
cd ~/dsmma_kn_23
source /home/cough052/barna314/anaconda3/bin/activate nmma_env
light_curve_analysis --data injections/lc_Me2017_00000.json --model nugent-hyper --label lc_Me2017_00000_fit_nugent-hyper_tmax_09 --prior ./priors/nugent-hyper.prior --svd-path ~/dsmma_kn_23/svdmodels --filters ztfg --tmin 0.1 --tmax 9.099999999999998 --dt 0.5 --trigger-time 44244.01022038909 --error-budget 1 --nlive 1024 --ztf-uncertainties --ztf-ToO 180 --outdir fits_msi/lc_Me2017_00000/nugent-hyper --plot --bestfit  --detection-limit "{'r':21.5, 'g':21.5, 'i':21.5}" --remove-nondetections --verbose