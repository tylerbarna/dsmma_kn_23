#!/bin/bash
#SBATCH --partition=shared
#SBATCH --account=umn131
#SBATCH --job-name=ZTF23absbqun
#SBATCH --time=01:59:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8gb
#SBATCH -o ~/dsmma_kn_23/specialCandidates/%x_%j.out
#SBATCH -e ~/dsmma_kn_23/specialCandidates/%x_%j.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=ztfrest@gmail.com
cd ~dsmma_kn_23/specialCandidates
source activate nmma_dev

lightcurve-analysis --data ~/dsmma_kn_23/specialCandidates/ZTF23absbqun.csv --model Me2017 --label ZTF23absbqun_Me2017 --prior /home/tbarna/dsmma_kn_23/priors/Me2017.prior --svd-path ~/dsmma_kn_23/svdmodels --filters ztfg,ztfr,ztfi --tmin 0.1 --tmax 21.0 --dt 0.5 --trigger-time 60245.45385 --error-budget 1 --nlive 1024 --ztf-uncertainties --ztf-ToO 180 --outdir ~/dsmma_kn_23/specialCandidates/ZTF23absbqun/ --bestfit  --detection-limit "{'r':21.5, 'g':21.5, 'i':21.5}" --remove-nondetections

lightcurve-analysis --data ~/dsmma_kn_23/specialCandidates/ZTF23absbqun.csv --model Bu2019lm --label ZTF23absbqun_Bu2019lm --prior /home/tbarna/dsmma_kn_23/priors/Bu2019lm.prior --svd-path ~/dsmma_kn_23/svdmodels --filters ztfg,ztfr,ztfi --tmin 0.1 --tmax 21.0 --dt 0.5 --trigger-time 60245.45385 --error-budget 1 --nlive 1024 --ztf-uncertainties --ztf-ToO 180 --outdir ~/dsmma_kn_23/specialCandidates/ZTF23absbqun/ --bestfit  --detection-limit "{'r':21.5, 'g':21.5, 'i':21.5}" --remove-nondetections

lightcurve-analysis --data ~/dsmma_kn_23/specialCandidates/ZTF23absbqun.csv --model TrPi2018 --label ZTF23absbqun_TrPi2018 --prior /home/tbarna/dsmma_kn_23/priors/TrPi2018.prior --svd-path ~/dsmma_kn_23/svdmodels --filters ztfg,ztfr,ztfi --tmin 0.1 --tmax 21.0 --dt 0.5 --trigger-time 60245.45385 --error-budget 1 --nlive 1024 --ztf-uncertainties --ztf-ToO 180 --outdir ~/dsmma_kn_23/specialCandidates/ZTF23absbqun/ --bestfit  --detection-limit "{'r':21.5, 'g':21.5, 'i':21.5}" --remove-nondetections

lightcurve-analysis --data ~/dsmma_kn_23/specialCandidates/ZTF23absbqun.csv --model nugent-hyper --label ZTF23absbqun_nugent-hyper --prior /home/tbarna/dsmma_kn_23/priors/nugent-hyper.prior --svd-path ~/dsmma_kn_23/svdmodels --filters ztfg,ztfr,ztfi --tmin 0.1 --tmax 21.0 --dt 0.5 --trigger-time 60245.45385 --error-budget 1 --nlive 1024 --ztf-uncertainties --ztf-ToO 180 --outdir ~/dsmma_kn_23/specialCandidates/ZTF23absbqun/ --bestfit  --detection-limit "{'r':21.5, 'g':21.5, 'i':21.5}" --remove-nondetections

lightcurve-analysis --data ~/dsmma_kn_23/specialCandidates/ZTF23absbqun.csv --model Piro2021 --label ZTF23absbqun_Piro2021 --prior /home/tbarna/dsmma_kn_23/priors/Piro2021.prior --svd-path ~/dsmma_kn_23/svdmodels --filters ztfg,ztfr,ztfi --tmin 0.1 --tmax 21.0 --dt 0.5 --trigger-time 60245.45385 --error-budget 1 --nlive 1024 --ztf-uncertainties --ztf-ToO 180 --outdir ~/dsmma_kn_23/specialCandidates/ZTF23absbqun/ --bestfit  --detection-limit "{'r':21.5, 'g':21.5, 'i':21.5}" --remove-nondetections