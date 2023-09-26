#!/bin/bash
#SBATCH --time=47:59:59
#SBATCH --mail-type=ALL
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=8gb
#NOTSBATCH -p amdsmall
#SBATCH --mail-type=ALL
#SBATCH --mail-user=ztfrest@gmail.com
#SBATCH -J calc_residuals
#SBATCH -o ./logs/%j.out
#SBATCH -e ./logs/%j.err

#source /home/cough052/barna314/anaconda3/bin/activate nmma
eval "$(conda shell.bash hook)"
conda activate nmma

#python3 /home/cough052/barna314/dsmma_kn_23/calc_residuals.py
python3 ./calc_residuals.py