#!/bin/bash
#SBATCH --job-name=T42_ape      # create a short name for your job
#SBATCH --exclusive             # important for performance!
#SBATCH --ntasks=32             # number of tasks per node
#SBATCH --cpus-per-task=1       # cpu-cores per task (>1 if multi-threaded tasks)
#SBATCH --time=8:00:00          # total run time limit (HH:MM:SS)

# source activate isca_env
python  ./control_ape.py
