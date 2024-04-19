#!/bin/bash
#SBATCH --job-name=ztfevalOrig
#SBATCH --time=47:59:59
#SBATCH --partition=shared
#SBATCH --account=umn131
#SBATCH --mail-type=ALL
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=12
#SBATCH --mem=32gb
#SBATCH -o ./logs/%x_%j.out
#SBATCH -e ./logs/%x_%j.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=ztfrest@gmail.com

source activate nmma_dev

echo "Evaluating ZTF-like cadences"

# echo "Running UCB evaluation for Me2017"
# python3 /home/tbarna/dsmma_kn_23/scaledBandit.py -m nugent-hyper Me2017 TrPi2018 -tm Me2017 --reward ucb --min-detections 7 --min-detections-cutoff 15 --nsteps 7 --outdir /expanse/lustre/projects/umn131/tbarna/ztfeval3/Me2017 --nsamples 10 --ztf-sampling --tstep 2

echo "Running UCB evaluation for Bu2019lm"
python3 /home/tbarna/dsmma_kn_23/scaledBandit.py -m nugent-hyper Bu2019lm TrPi2018 -tm Bu2019lm --reward ucb --min-detections 8 --min-detections-cutoff 18 --nsteps 7 --outdir /expanse/lustre/projects/umn131/tbarna/ztfevalPaper/Bu2019lm --nsamples 100 --ztf-sampling --tstep 2 