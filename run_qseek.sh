#!/bin/bash
#SBATCH --job-name=qseek # create a name for your job
#SBATCH --partition=shared-cpu,public-cpu,public-bigmem,shared-bigmem
#SBATCH --ntasks=1               # total number of tasks
#SBATCH --cpus-per-task=50      # cpu-cores per task
##SBATCH --mem=35G         # memory per cpu-core
#SBATCH --time=12:00:00          # total run time limit (HH:MM:SS)
#SBATCH --output="outslurm/%x-%j.out"

source /opt/ebsofts/Anaconda3/2021.05/etc/profile.d/conda.sh
conda activate qseek

qseek search my-search.json
