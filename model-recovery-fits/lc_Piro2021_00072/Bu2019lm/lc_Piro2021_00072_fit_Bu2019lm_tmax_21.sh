#!/bin/bash
#SBATCH --partition=shared
#SBATCH --account=umn131
#SBATCH --job-name=lc_Piro2021_00072_fit_Bu2019lm_tmax_21
#SBATCH --time=23:59:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8gb
#SBATCH -o model-recovery-fits/lc_Piro2021_00072/Bu2019lm/%x_%j.out
#SBATCH -e model-recovery-fits/lc_Piro2021_00072/Bu2019lm/%x_%j.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=ztfrest@gmail.com
cd ~/dsmma_kn_23
source activate nmma_env
light_curve_analysis --data model-recovery-injections/lc_Piro2021_00072.json --model Bu2019lm --label lc_Piro2021_00072_fit_Bu2019lm_tmax_21 --prior ./priors/Bu2019lm.prior --svd-path ~/dsmma_kn_23/svdmodels --filters ztfg --tmin 0.1 --tmax 21 --dt 0.5 --trigger-time 44243.01204298015 --error-budget 1 --nlive 1024 --ztf-uncertainties --ztf-ToO 180 --outdir model-recovery-fits/lc_Piro2021_00072/Bu2019lm --plot --bestfit  --detection-limit "{'r':21.5, 'g':21.5, 'i':21.5}" --remove-nondetections --verbose