#!/bin/bash
#SBATCH --partition=shared
#SBATCH --account=umn131
#SBATCH --job-name=lc_ZTF23absbqun_ztf-sedm_fit_TrPi2018_tmax_03
#SBATCH --time=01:59:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8gb
#SBATCH -o ./specialFits/lc_ZTF23absbqun_ztf-sedm/TrPi2018/%x_%j.out
#SBATCH -e ./specialFits/lc_ZTF23absbqun_ztf-sedm/TrPi2018/%x_%j.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=ztfrest@gmail.com
cd /expanse/lustre/projects/umn131/tbarna/
source activate nmma_dev
lightcurve-analysis --data /home/tbarna/dsmma_kn_23/specialCandidates/lc_ZTF23absbqun_ztf-sedm.json --model TrPi2018 --label lc_ZTF23absbqun_ztf-sedm_fit_TrPi2018_tmax_03 --prior ~/dsmma_kn_23/priors/TrPi2018.prior --svd-path ~/dsmma_kn_23/svdmodels --filters ztfg,ztfr,sdssg,sdssi,sdssr --tmin 0.1 --tmax 3.1 --dt 0.5 --trigger-time 60285.23201389983 --error-budget 1 --nlive 1024 --ztf-uncertainties --ztf-ToO 180 --outdir ./specialFits/lc_ZTF23absbqun_ztf-sedm/TrPi2018 --bestfit  --detection-limit "{'r':21.5, 'g':21.5, 'i':21.5}" --remove-nondetections