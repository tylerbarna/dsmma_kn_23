#!/bin/bash
#SBATCH --partition=shared
#SBATCH --account=umn131
#SBATCH --job-name=model-recovery-ignore-first-test
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

python3 analysis_script.py --data ~/dsmma_kn_23/injections/model-recovery-validated-injections --outdir /expanse/lustre/projects/umn131/tbarna/model-recovery-ignore-first --priors ~/dsmma_kn_23/priors --env nmma_dev  --cluster expanse --models nugent-hyper --tmin 3.1 --tmax 4.1 --tstep 1 --timeout 4 --nmma-tmin 1.0 --nmma-plot

python3 analysis_script.py --data ~/dsmma_kn_23/injections/model-recovery-validated-injections --outdir /expanse/lustre/projects/umn131/tbarna/model-recovery-ignore-first --priors ~/dsmma_kn_23/priors --env nmma_dev --cluster expanse --models Bu2019lm --tmin 3.1 --tmax 4.1 --tstep 1 --timeout 4 --nmma-tmin 1.0 --nmma-plot

python3 analysis_script.py --data ~/dsmma_kn_23/injections/model-recovery-validated-injections --outdir /expanse/lustre/projects/umn131/tbarna/model-recovery-ignore-first --priors ~/dsmma_kn_23/priors --env nmma_dev --cluster expanse --models TrPi2018 --tmin 3.1 --tmax 4.1 --tstep 1 --timeout 4 --nmma-tmin 1.0 --nmma-plot

python3 analysis_script.py --data ~/dsmma_kn_23/injections/model-recovery-validated-injections --outdir /expanse/lustre/projects/umn131/tbarna/model-recovery-ignore-first --priors ~/dsmma_kn_23/priors --env nmma_dev --cluster expanse --models Piro2021 --tmin 3.1 --tmax 4.1 --tstep 1 --timeout 4 --nmma-tmin 1.0 --nmma-plot



python3 analysis_script.py --data ~/dsmma_kn_23/injections/model-recovery-validated-injections --outdir /expanse/lustre/projects/umn131/tbarna/model-recovery-ignore-first --priors ~/dsmma_kn_23/priors --env nmma_dev  --cluster expanse --models nugent-hyper --tmin 7.1 --tmax 8.1 --tstep 1 --timeout 4 --nmma-tmin 1.0 --nmma-plot

python3 analysis_script.py --data ~/dsmma_kn_23/injections/model-recovery-validated-injections --outdir /expanse/lustre/projects/umn131/tbarna/model-recovery-ignore-first --priors ~/dsmma_kn_23/priors --env nmma_dev --cluster expanse --models Bu2019lm --tmin 7.1 --tmax 8.1 --tstep 1 --timeout 4 --nmma-tmin 1.0 --nmma-plot

python3 analysis_script.py --data ~/dsmma_kn_23/injections/model-recovery-validated-injections --outdir /expanse/lustre/projects/umn131/tbarna/model-recovery-ignore-first --priors ~/dsmma_kn_23/priors --env nmma_dev --cluster expanse --models TrPi2018 --tmin 7.1 --tmax 8.1 --tstep 1 --timeout 4 --nmma-tmin 1.0 --nmma-plot

python3 analysis_script.py --data ~/dsmma_kn_23/injections/model-recovery-validated-injections --outdir /expanse/lustre/projects/umn131/tbarna/model-recovery-ignore-first --priors ~/dsmma_kn_23/priors --env nmma_dev --cluster expanse --models Piro2021 --tmin 7.1 --tmax 8.1 --tstep 1 --timeout 4 --nmma-tmin 1.0 --nmma-plot



python3 analysis_script.py --data ~/dsmma_kn_23/injections/model-recovery-validated-injections --outdir /expanse/lustre/projects/umn131/tbarna/model-recovery-ignore-first --priors ~/dsmma_kn_23/priors --env nmma_dev  --cluster expanse --models nugent-hyper --tmin 10.1 --tmax 11.1 --tstep 1 --timeout 4 --nmma-tmin 1.0 --nmma-plot

python3 analysis_script.py --data ~/dsmma_kn_23/injections/model-recovery-validated-injections --outdir /expanse/lustre/projects/umn131/tbarna/model-recovery-ignore-first --priors ~/dsmma_kn_23/priors --env nmma_dev --cluster expanse --models Bu2019lm --tmin 10.1 --tmax 11.1 --tstep 1 --timeout 4 --nmma-tmin 1.0 --nmma-plot

python3 analysis_script.py --data ~/dsmma_kn_23/injections/model-recovery-validated-injections --outdir /expanse/lustre/projects/umn131/tbarna/model-recovery-ignore-first --priors ~/dsmma_kn_23/priors --env nmma_dev --cluster expanse --models TrPi2018 --tmin 10.1 --tmax 11.1 --tstep 1 --timeout 4 --nmma-tmin 1.0 --nmma-plot

python3 analysis_script.py --data ~/dsmma_kn_23/injections/model-recovery-validated-injections --outdir /expanse/lustre/projects/umn131/tbarna/model-recovery-ignore-first --priors ~/dsmma_kn_23/priors --env nmma_dev --cluster expanse --models Piro2021 --tmin 10.1 --tmax 11.1 --tstep 1 --timeout 4 --nmma-tmin 1.0 --nmma-plot



python3 analysis_script.py --data ~/dsmma_kn_23/injections/model-recovery-validated-injections --outdir /expanse/lustre/projects/umn131/tbarna/model-recovery-ignore-first --priors ~/dsmma_kn_23/priors --env nmma_dev  --cluster expanse --models nugent-hyper --tmin 21 --tmax 21.1 --tstep 1 --timeout 4 --nmma-tmin 1.0 --nmma-plot

python3 analysis_script.py --data ~/dsmma_kn_23/injections/model-recovery-validated-injections --outdir /expanse/lustre/projects/umn131/tbarna/model-recovery-ignore-first --priors ~/dsmma_kn_23/priors --env nmma_dev --cluster expanse --models Bu2019lm --tmin 21 --tmax 21.1 --tstep 1 --timeout 4 --nmma-tmin 1.0 --nmma-plot

python3 analysis_script.py --data ~/dsmma_kn_23/injections/model-recovery-validated-injections --outdir /expanse/lustre/projects/umn131/tbarna/model-recovery-ignore-first --priors ~/dsmma_kn_23/priors --env nmma_dev --cluster expanse --models TrPi2018 --tmin 21 --tmax 21.1 --tstep 1 --timeout 4 --nmma-tmin 1.0 --nmma-plot

python3 analysis_script.py --data ~/dsmma_kn_23/injections/model-recovery-validated-injections --outdir /expanse/lustre/projects/umn131/tbarna/model-recovery-ignore-first --priors ~/dsmma_kn_23/priors --env nmma_dev --cluster expanse --models Piro2021 --tmin 21 --tmax 21.1 --tstep 1 --timeout 4 --nmma-tmin 1.0 --nmma-plot



echo "All done with analysis!"

# python3 ./requeue.py --test-run --root-dir /expanse/lustre/projects/umn131/tbarna/model-recovery-ignore-first --output-file ./failures/model-recovery-timestep-failures --stats

python3 utils/evaluation.py --lc-path ~/dsmma_kn_23/injections/model-recovery-validated-injections --fit-path /expanse/lustre/projects/umn131/tbarna/model-recovery-ignore-first --output ./fit_dataframes/model-recovery-ignore-first-fit_df.csv

echo "All done with evaluation!"