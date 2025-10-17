#!/bin/bash
#SBATCH --job-name=uniformT170         # create a short name for your job
#SBATCH --exclusive             # important for performance!
#SBATCH --ntasks=128             # number of tasks per node
#SBATCH --cpus-per-task=1       # cpu-cores per task (>1 if multi-threaded tasks)
#SBATCH --time=16:00:00          # total run time limit (HH:MM:SS)

# source activate isca_env
python  ./uniformT170.py

