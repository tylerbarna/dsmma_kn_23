#!/bin/bash
#SBATCH --partition=shared
#SBATCH --account=umn131
#SBATCH --job-name=toy-model-validated
#SBATCH --time=23:59:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=8gb
#SBATCH -o ./logs/%x_%j.out
#SBATCH -e ./logs/%x_%j.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=ztfrest@gmail.com
cd ~/dsmma_kn_23
source activate nmma_dev

python3 generation_script.py --outdir ~dsmma_kn_23/injections/toy-model-injections/

python3 analysis_script.py --data ~/dsmma_kn_23/injections/toy-model-injections/ --outdir /expanse/lustre/projects/umn131/tbarna/toy-model-fits/ --priors ~/dsmma_kn_23/priors --env nmma_dev  --cluster expanse --models nugent-hyper Me2017 TrPi2018 --tmin 3.1 --tmax 21.1 --tstep 2 --timeout 4

echo "All done with analysis!"

python3 utils/evaluation.py --lc-path ~/dsmma_kn_23/injections/toy-model-injections/ --fit-path /expanse/lustre/projects/umn131/tbarna/toy-model-fits/ --output ./fit_dataframes/toy-model-fit_df.csv

echo "All done with evaluation!"
