#!/bin/bash

#SBATCH --nodes=1
#SBATCH -n 4
#SBATCH --time=24:00:00
#SBATCH -p defq
#SBATCH --mail-type=ALL
#SBATCH --mail-user=mpeeks@mit.edu
#SBATCH --mem=55000
#SBATCH --exclusive

set INT=i8

(echo %rwf=${TMPDIR}/${SLURM_JOB_NAME}.rwf ; echo %NoSave; cat ${SLURM_JOB_NAME}.com ) | g09 > ${SLURM_JOB_NAME}.log

