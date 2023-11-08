#!/bin/bash
#SBATCH --partition=shared
#SBATCH --account=umn131
#SBATCH --job-name=model-recovery-21
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

python3 analysis_script.py --data ~/dsmma_kn_23/injections/model-recovery-validated-injections --outdir /expanse/lustre/projects/umn131/tbarna/model-recovery-ignore-first-21 --priors ~/dsmma_kn_23/priors --env nmma_dev  --cluster expanse --models nugent-hyper --tmin 21.1 --tmax 22 --tstep 1 --timeout 4 --nmma-tmin 1.5 --nmma-plot

python3 analysis_script.py --data ~/dsmma_kn_23/injections/model-recovery-validated-injections --outdir /expanse/lustre/projects/umn131/tbarna/model-recovery-ignore-first-21 --priors ~/dsmma_kn_23/priors --env nmma_dev --cluster expanse --models Bu2019lm --tmin 21.1 --tmax 22 --tstep 1 --timeout 4 --nmma-tmin 1.5 --nmma-plot

python3 analysis_script.py --data ~/dsmma_kn_23/injections/model-recovery-validated-injections --outdir /expanse/lustre/projects/umn131/tbarna/model-recovery-ignore-first-21 --priors ~/dsmma_kn_23/priors --env nmma_dev --cluster expanse --models TrPi2018 --tmin 21.1 --tmax 22 --tstep 1 --timeout 4 --nmma-tmin 1.5 --nmma-plot

python3 analysis_script.py --data ~/dsmma_kn_23/injections/model-recovery-validated-injections --outdir /expanse/lustre/projects/umn131/tbarna/model-recovery-ignore-first-21 --priors ~/dsmma_kn_23/priors --env nmma_dev --cluster expanse --models Piro2021 --tmin 21.1 --tmax 22 --tstep 1 --timeout 4 --nmma-tmin 1.5 --nmma-plot

echo "All done with analysis!"

# python3 ./requeue.py --test-run --root-dir /expanse/lustre/projects/umn131/tbarna/model-recovery-ignore-first-21 --output-file ./failures/model-recovery-timestep-failures --stats

python3 utils/evaluation.py --lc-path ~/dsmma_kn_23/injections/model-recovery-validated-injections --fit-path /expanse/lustre/projects/umn131/tbarna/model-recovery-ignore-first-21 --output ./fit_dataframes/model-recovery-ignore-first-21-fit_df.csv

echo "All done with evaluation!"