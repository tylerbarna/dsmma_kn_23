#!/bin/bash
#SBATCH --job-name=ucbeval
#SBATCH --time=71:59:59
#SBATCH --mail-type=ALL
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=8gb
#NOTSBATCH -p amdsmall
#SBATCH -o ./logs/%x_%j.out
#SBATCH -e ./logs/%x_%j.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=ztfrest@gmail.com

source /home/cough052/barna314/anaconda3/bin/activate nmma_dev

echo "Running UCB evaluation for Me2017"
# Me2017

# do with ucb
echo "Running with UCB"
python3 /home/cough052/barna314/dsmma_kn_23/scaledBandit.py -m nugent-hyper Me2017 TrPi2018 -tm Me2017 --reward ucb --min-detections 15 --min-detections-cutoff 10 --nsteps 7 --outdir /expanse/lustre/projects/umn131/tbarna/ucbeval/Me2017/ucb 

# do without
echo "Running without UCB"
python3 /home/cough052/barna314/dsmma_kn_23/scaledBandit.py -m nugent-hyper Me2017 TrPi2018 -tm Me2017 --reward none --min-detections 15 --min-detections-cutoff 10 --nsteps 7 --outdir /expanse/lustre/projects/umn131/tbarna/ucbeval/Me2017/no_ucb

# Bu2019lm

echo "Running UCB evaluation for Bu2019lm"

# do with ucb
echo "Running with UCB"
python3 /home/cough052/barna314/dsmma_kn_23/scaledBandit.py -m nugent-hyper Bu2019lm TrPi2018 -tm Bu2019lm --reward ucb --min-detections 15 --min-detections-cutoff 10 --nsteps 7 --outdir /expanse/lustre/projects/umn131/tbarna/ucbeval/Bu2019lm/ucb 

# do without
echo "Running without UCB"
python3 /home/cough052/barna314/dsmma_kn_23/scaledBandit.py -m nugent-hyper Bu2019lm TrPi2018 -tm Bu2019lm --reward none --min-detections 15 --min-detections-cutoff 10 --nsteps 7 --outdir /expanse/lustre/projects/umn131/tbarna/ucbeval/Bu2019lm/no_ucb