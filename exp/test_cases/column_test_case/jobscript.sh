#!/bin/bash
#SBATCH --job-name=rrtm_column_test # create a short name for your job
#SBATCH --exclusive             # important for performance!
#SBATCH --ntasks=16             # number of tasks per node
#SBATCH --cpus-per-task=1       # cpu-cores per task (>1 if multi-threaded tasks)
#SBATCH --time=1:00:00          # total run time limit (HH:MM:SS)

rm -r /home/cyinchang/archive/cyinchang03/Isca/column_test

source activate isca_fenv
python ./column_test_rrtm.py