#!/bin/bash
#SBATCH --job-name=Q_col        # create a short name for your job
#SBATCH --exclusive             # important for performance!
#SBATCH --ntasks=32             # number of tasks per node
#SBATCH --cpus-per-task=1       # cpu-cores per task (>1 if multi-threaded tasks)
#SBATCH --time=8:00:00          # total run time limit (HH:MM:SS)

tau_bm=7200
xtimes=1
# source activate isca_env
python  ./column_ent.py
