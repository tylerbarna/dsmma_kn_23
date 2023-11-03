#!/bin/bash
#SBATCH --partition=shared
#SBATCH --account=umn131
#SBATCH --job-name=lc_TrPi2018_00037_fit_TrPi2018_tmax_21
#SBATCH --time=01:59:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8gb
#SBATCH -o /home/tbarna/dsmma_kn_23/presentation_TrPi2018/lc_TrPi2018_00037/TrPi2018/%x_%j.out
#SBATCH -e /home/tbarna/dsmma_kn_23/presentation_TrPi2018/lc_TrPi2018_00037/TrPi2018/%x_%j.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=ztfrest@gmail.com
cd /home/tbarna/dsmma_kn_23/presentation_TrPi2018/lc_TrPi2018_00037/TrPi2018
source activate nmma_dev
lightcurve-analysis --data /home/tbarna/dsmma_kn_23/presentation_TrPi2018/lc_TrPi2018_00037.json --model TrPi2018 --label lc_TrPi2018_00037_fit_TrPi2018_tmax_21 --prior /home/tbarna/dsmma_kn_23/priors/TrPi2018.prior --svd-path ~/dsmma_kn_23/svdmodels --filters ztfg --tmin 0.1 --tmax 21 --dt 0.5 --trigger-time 44244.007343275014 --error-budget 1 --nlive 1024 --ztf-uncertainties --ztf-ToO 180 --outdir ./ --bestfit  --detection-limit "{'r':21.5, 'g':21.5, 'i':21.5}" --remove-nondetections --plot