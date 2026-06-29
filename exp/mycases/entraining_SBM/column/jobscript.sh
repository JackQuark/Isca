#!/bin/bash
#SBATCH --job-name=Q_col
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --time=8:00:00
#SBATCH --export=ALL

# source activate isca_fenv
python ./control_col.py