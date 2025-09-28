#!/bin/bash
#SBATCH --job-name=HST42        # create a short name for your job
#SBATCH --exclusive             # important for performance!
#SBATCH --ntasks=16             # number of tasks per node
#SBATCH --cpus-per-task=1       # cpu-cores per task (>1 if multi-threaded tasks)
#SBATCH --time=1:00:00          # total run time limit (HH:MM:SS)
#SBATCH --mail-type=all         # send email for all events during the job
#SBATCH --mail-user=yen169054@gmail.com

source activate isca_fenv
python  ./held_suarez_test_case.py