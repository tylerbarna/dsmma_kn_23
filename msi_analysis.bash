#!/bin/bash


#SBATCH --mail-type=ALL
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8gb
#SBATCH -p amdsmall
#SBATCH -o %j.out
#SBATCH -e %j.err

source /home/cough052/barna314/anaconda3/bin/activate nmma

python /panfs/roc/groups/7/cough052/barna314/dsmma_kn_23/lightcurve_analysis.py --datafile "$1" --candname "$2" --model "$3" --prior "$4"  --nlive 128 --cpus 4