#!/bin/bash
#SBATCH --partition=shared
#SBATCH --account=umn131
#SBATCH --job-name=model-recovery-timestep-test
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

python3 analysis_script.py --data ~/dsmma_kn_23/injections/model-recovery-validated-injections --outdir /expanse/lustre/projects/umn131/tbarna/model-recovery-validated-fits --priors ~/dsmma_kn_23/priors --env nmma_dev  --cluster expanse --models nugent-hyper --tmin 3.1 --tmax 3.1 --tstep 1 --timeout 4 --dry-run