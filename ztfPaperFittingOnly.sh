#!/bin/bash
#SBATCH --job-name=ztfFittingOnly
#SBATCH --time=47:59:59
#SBATCH --partition=shared
#SBATCH --account=umn131
#SBATCH --mail-type=ALL
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=40gb
#SBATCH -o ./logs/%x_%j.out
#SBATCH -e ./logs/%x_%j.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=ztfrest@gmail.com

source activate nmma_dev

echo "Evaluating ZTF-like cadences"


echo "Running UCB evaluation for Bu2019lm"
python3 /home/tbarna/dsmma_kn_23/scaledBandit_fit_only.py -m nugent-hyper Bu2019lm TrPi2018 -tm Bu2019lm --reward ucb --min-detections 7 --min-detections-cutoff 18 --nsteps 7 --outdir /expanse/lustre/projects/umn131/tbarna/ztfevalPaper/Bu2019lm --nsamples 100 --ztf-sampling --tstep 2 
