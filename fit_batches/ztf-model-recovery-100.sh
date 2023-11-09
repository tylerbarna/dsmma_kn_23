#!/bin/bash
#SBATCH --partition=shared
#SBATCH --account=umn131
#SBATCH --job-name=ztf-model-recovery-100
#SBATCH --time=35:59:00
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

echo "Generating injections..."
python3 generation_script.py --models Bu2019lm nugent-hyper TrPi2018 Piro2021 --outdir ./injections/ztf-cadence-100 --min-detections 3 --min-detections-cutoff 5 --multiplier 100 --ztf-sampling 


echo "Running analysis..."
python3 analysis_script.py --data ~/dsmma_kn_23/injections/ztf-cadence-100 --outdir /expanse/lustre/projects/umn131/tbarna/ztf-cadence-100-fits --priors ~/dsmma_kn_23/priors --env nmma_dev  --cluster expanse --models nugent-hyper --tmin 2 --tmax 3.1 --tstep 1 --timeout 4

python3 analysis_script.py --data ~/dsmma_kn_23/injections/ztf-cadence-100 --outdir /expanse/lustre/projects/umn131/tbarna/ztf-cadence-100-fits  --priors ~/dsmma_kn_23/priors --env nmma_dev --cluster expanse --models Bu2019lm --tmin 2 --tmax 3.1 --tstep 1 --timeout 4

python3 analysis_script.py --data ~/dsmma_kn_23/injections/ztf-cadence-100 --outdir /expanse/lustre/projects/umn131/tbarna/ztf-cadence-100-fits  --priors ~/dsmma_kn_23/priors --env nmma_dev --cluster expanse --models TrPi2018 --tmin 2 --tmax 3.1 --tstep 1 --timeout 4

python3 analysis_script.py --data ~/dsmma_kn_23/injections/ztf-cadence-100 --outdir /expanse/lustre/projects/umn131/tbarna/ztf-cadence-100-fits  --priors ~/dsmma_kn_23/priors --env nmma_dev --cluster expanse --models Piro2021 --tmin 2 --tmax 3.1 --tstep 1 --timeout 4



python3 analysis_script.py --data ~/dsmma_kn_23/injections/ztf-cadence-100 --outdir /expanse/lustre/projects/umn131/tbarna/ztf-cadence-100-fits --priors ~/dsmma_kn_23/priors --env nmma_dev  --cluster expanse --models nugent-hyper --tmin 5 --tmax 5.1 --tstep 1 --timeout 4

python3 analysis_script.py --data ~/dsmma_kn_23/injections/ztf-cadence-100 --outdir /expanse/lustre/projects/umn131/tbarna/ztf-cadence-100-fits  --priors ~/dsmma_kn_23/priors --env nmma_dev --cluster expanse --models Bu2019lm --tmin 5 --tmax 5.1 --tstep 1 --timeout 4

python3 analysis_script.py --data ~/dsmma_kn_23/injections/ztf-cadence-100 --outdir /expanse/lustre/projects/umn131/tbarna/ztf-cadence-100-fits  --priors ~/dsmma_kn_23/priors --env nmma_dev --cluster expanse --models TrPi2018 --tmin 5 --tmax 5.1 --tstep 1 --timeout 4

python3 analysis_script.py --data ~/dsmma_kn_23/injections/ztf-cadence-100 --outdir /expanse/lustre/projects/umn131/tbarna/ztf-cadence-100-fits  --priors ~/dsmma_kn_23/priors --env nmma_dev --cluster expanse --models Piro2021 --tmin 5 --tmax 5.1 --tstep 1 --timeout 4



python3 analysis_script.py --data ~/dsmma_kn_23/injections/ztf-cadence-100 --outdir /expanse/lustre/projects/umn131/tbarna/ztf-cadence-100-fits --priors ~/dsmma_kn_23/priors --env nmma_dev  --cluster expanse --models nugent-hyper --tmin 10 --tmax 10.1 --tstep 1 --timeout 4

python3 analysis_script.py --data ~/dsmma_kn_23/injections/ztf-cadence-100 --outdir /expanse/lustre/projects/umn131/tbarna/ztf-cadence-100-fits  --priors ~/dsmma_kn_23/priors --env nmma_dev --cluster expanse --models Bu2019lm --tmin 10 --tmax 10.1 --tstep 1 --timeout 4

python3 analysis_script.py --data ~/dsmma_kn_23/injections/ztf-cadence-100 --outdir /expanse/lustre/projects/umn131/tbarna/ztf-cadence-100-fits  --priors ~/dsmma_kn_23/priors --env nmma_dev --cluster expanse --models TrPi2018 --tmin 10 --tmax 10.1 --tstep 1 --timeout 4

python3 analysis_script.py --data ~/dsmma_kn_23/injections/ztf-cadence-100 --outdir /expanse/lustre/projects/umn131/tbarna/ztf-cadence-100-fits  --priors ~/dsmma_kn_23/priors --env nmma_dev --cluster expanse --models Piro2021 --tmin 10 --tmax 10.1 --tstep 1 --timeout 4



python3 analysis_script.py --data ~/dsmma_kn_23/injections/ztf-cadence-100 --outdir /expanse/lustre/projects/umn131/tbarna/ztf-cadence-100-fits --priors ~/dsmma_kn_23/priors --env nmma_dev  --cluster expanse --models nugent-hyper --tmin 21 --tmax 21.1 --tstep 1 --timeout 4

python3 analysis_script.py --data ~/dsmma_kn_23/injections/ztf-cadence-100 --outdir /expanse/lustre/projects/umn131/tbarna/ztf-cadence-100-fits  --priors ~/dsmma_kn_23/priors --env nmma_dev --cluster expanse --models Bu2019lm --tmin 21 --tmax 21.1 --tstep 1 --timeout 4

python3 analysis_script.py --data ~/dsmma_kn_23/injections/ztf-cadence-100 --outdir /expanse/lustre/projects/umn131/tbarna/ztf-cadence-100-fits  --priors ~/dsmma_kn_23/priors --env nmma_dev --cluster expanse --models TrPi2018 --tmin 21 --tmax 21.1 --tstep 1 --timeout 4

python3 analysis_script.py --data ~/dsmma_kn_23/injections/ztf-cadence-100 --outdir /expanse/lustre/projects/umn131/tbarna/ztf-cadence-100-fits  --priors ~/dsmma_kn_23/priors --env nmma_dev --cluster expanse --models Piro2021 --tmin 21 --tmax 21.1 --tstep 1 --timeout 4

echo "Analysis Complete!"

echo "Searching for failed jobs..."
python3 ./requeue.py --test-run --root-dir /expanse/lustre/projects/umn131/tbarna/ztf-cadence-100-fits  --output-file ./failures/ztf-cadence-100-failures --stats

echo "Evaluating analyses..."
python3 utils/evaluation.py --lc-path ~/dsmma_kn_23/injections/ztf-cadence-100 --fit-path /expanse/lustre/projects/umn131/tbarna/ztf-cadence-100-fits  --output ./fit_dataframes/ztf-cadence-100-fit_df.csv

echo "All done with evaluation!"