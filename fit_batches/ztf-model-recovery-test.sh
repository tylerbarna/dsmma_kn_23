#!/bin/bash
#SBATCH --partition=shared
#SBATCH --account=umn131
#SBATCH --job-name=ztf-model-recovery-test
#SBATCH --time=23:59:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8gb
#SBATCH -o ./logs/%x_%j.out
#SBATCH -e ./logs/%x_%j.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=ztfrest@gmail.com
cd ~/dsmma_kn_23
source activate nmma_dev

python3 analysis_script.py --data ~/dsmma_kn_23/injections/ztf-cadence-test --outdir /expanse/lustre/projects/umn131/tbarna/ztf-cadence-test-fits --priors ~/dsmma_kn_23/priors --env nmma_dev  --cluster expanse --models nugent-hyper --tmin 21 --tmax 21.1 --tstep 1 --timeout 4

python3 analysis_script.py --data ~/dsmma_kn_23/injections/ztf-cadence-test --outdir /expanse/lustre/projects/umn131/tbarna/ztf-cadence-test-fits  --priors ~/dsmma_kn_23/priors --env nmma_dev --cluster expanse --models Bu2019lm --tmin 21 --tmax 21.1 --tstep 1 --timeout 4

python3 analysis_script.py --data ~/dsmma_kn_23/injections/ztf-cadence-test --outdir /expanse/lustre/projects/umn131/tbarna/ztf-cadence-test-fits  --priors ~/dsmma_kn_23/priors --env nmma_dev --cluster expanse --models TrPi2018 --tmin 21 --tmax 21.1 --tstep 1 --timeout 4

python3 analysis_script.py --data ~/dsmma_kn_23/injections/ztf-cadence-test --outdir /expanse/lustre/projects/umn131/tbarna/ztf-cadence-test-fits  --priors ~/dsmma_kn_23/priors --env nmma_dev --cluster expanse --models Piro2021 --tmin 21 --tmax 21.1 --tstep 1 --timeout 4

echo "All done with analysis!"

python3 ./requeue.py --test-run --root-dir /expanse/lustre/projects/umn131/tbarna/ztf-cadence-test-fits  --output-file ./failures/ztf-cadence-test-failures --stats

python3 utils/evaluation.py --lc-path ~/dsmma_kn_23/injections/ztf-cadence-test --fit-path /expanse/lustre/projects/umn131/tbarna/ztf-cadence-test-fits  --output ./fit_dataframes/ztf-cadence-test-fit_df.csv

echo "All done with evaluation!"