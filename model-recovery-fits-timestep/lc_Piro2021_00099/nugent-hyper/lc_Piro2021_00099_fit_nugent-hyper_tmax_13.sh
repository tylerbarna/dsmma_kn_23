#!/bin/bash
#SBATCH --job-name=lc_Piro2021_00099_fit_nugent-hyper_tmax_13
#SBATCH --time=23:59:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8gb
#SBATCH -o model-recovery-fits-timestep/lc_Piro2021_00099/nugent-hyper/%x_%j.out
#SBATCH -e model-recovery-fits-timestep/lc_Piro2021_00099/nugent-hyper/%x_%j.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=ztfrest@gmail.com
cd /expanse/lustre/projects/umn131/tbarna/
source /home/cough052/barna314/anaconda3/bin/activate nmma_dev
lightcurve-analysis --data /home/tbarna/dsmma_kn_23/model-recovery-injections/lc_Piro2021_00099.json --model nugent-hyper --label lc_Piro2021_00099_fit_nugent-hyper_tmax_13 --prior /home/tbarna/dsmma_kn_23/priors/nugent-hyper.prior --svd-path ~/dsmma_kn_23/svdmodels --filters ztfg --tmin 0.1 --tmax 13.099999999999998 --dt 0.5 --trigger-time 44243.708216557825 --error-budget 1 --nlive 1024 --ztf-uncertainties --ztf-ToO 180 --outdir model-recovery-fits-timestep/lc_Piro2021_00099/nugent-hyper --bestfit  --detection-limit "{'r':21.5, 'g':21.5, 'i':21.5}" --remove-nondetections --verbose