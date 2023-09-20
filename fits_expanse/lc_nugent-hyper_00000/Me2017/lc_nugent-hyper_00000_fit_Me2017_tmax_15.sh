#!/bin/bash
#SBATCH --partition=shared
#SBATCH --account=umn131
#SBATCH --job-name=lc_nugent-hyper_00000_fit_Me2017_tmax_15
#SBATCH --time=23:59:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8gb
#SBATCH -o ./fits_expanse/lc_nugent-hyper_00000/Me2017/%x_%j.out
#SBATCH -e ./fits_expanse/lc_nugent-hyper_00000/Me2017/%x_%j.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=ztfrest@gmail.com
cd ~/dsmma_kn_23
source activate nmma_env
light_curve_analysis --data ./injections/lc_nugent-hyper_00000.json --model Me2017 --label lc_nugent-hyper_00000_fit_Me2017_tmax_15 --prior ./priors/Me2017.prior --svd-path ~/dsmma_kn_23/svdmodels --filters ztfg --tmin 0.1 --tmax 15.099999999999996 --dt 0.5 --trigger-time 44244.01022041292 --error-budget 1 --nlive 1024 --ztf-uncertainties --ztf-ToO 180 --outdir ./fits_expanse/lc_nugent-hyper_00000/Me2017 --plot --bestfit  --detection-limit "{'r':21.5, 'g':21.5, 'i':21.5}" --remove-nondetections --verbose