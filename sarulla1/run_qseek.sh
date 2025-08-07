#!/bin/bash
#SBATCH --job-name=qseek # create a name for your job
#SBATCH --partition=shared-gpu,public-gpu ##,public-bigmem,shared-bigmem
#SBATCH --ntasks=1               # total number of tasks
#SBATCH --cpus-per-task=20
#SBATCH --gpus-per-task=5      # cpu-cores per task
##SBATCH --mem=35G         # memory per cpu-core
#SBATCH --time=12:00:00          # total run time limit (HH:MM:SS)
#SBATCH --output="outslurm/%x-%j.out"

source ~/.bashrc
conda activate qseek

qseek search my-search.json
