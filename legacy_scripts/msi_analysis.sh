#!/bin/bash
#SBATCH --name=msi_analysis
#SBATCH --time=23:59:59
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

source /home/cough052/barna314/anaconda3/bin/activate nmma

python3 /home/cough052/barna314/dsmma_kn_23/lightcurve_analysis.py --datafile "$1" --candname "$2" --model "$3" --prior "$4" --outdir "$5" --nlive 1024 --cpus 2

