#!/bin/bash

#############################################
#
# v 0.1 20190304
# Martin D Peeks
# martinp23@gmail.com
#
# This script does the following:
# 1. Copies files to $SCRATCH
# 2. Runs Gaussian (g16, but it's easy to change to g09). Writes the log file to the "slurm.out" file
#    on $DATA, but writes everything else to $SCRATCH
# 3. If the job finishes (either successfully or failed), copies back job files to $DATA
# 4. 30 mins before the job is due to end, this script kills Gaussian and copies all files back to $DATA.
#    This means that nothing should be lost if a job runs longer than expected.
# 5. Deletes our files in the scratch directory
#
# To run a job using this script, your jobfile should have the extension ".com". Your jobfile should *not*
# contain any %NoSave lines or a %rwf line. For a jobfile test.com, queue it using (after changing the
# desired job time as usual in the sh file):
#
#      sbatch --job-name test run-slurm-mpeeks.sh
#
# If you want to stop a job before it runs out of time or finishes, don't just use scancel. The chk
# will not be returned to you if you do that. Instead run:
#
#     scancel -b -s USR1 jobid    (jobid is the numerical job id).
#
# Please be sure to delete rwf/chk files which you don't need once a job finishes.
#
# Finally: note that this job copies *all* files in the submission directory to $SCRATCH.
# So you must run each job in its own folder - don't run multiple jobs per folder, because it
# wastes space and you might run into strange conflicts.
#
#
#   To recieve job status emails, add these lines to the #SBATCH block just after these comments
#
#   #SBATCH --mail-type=ALL
#   #SBATCH --mail-user=your@email.here.ox.ac.uk
#
#
#
################################################

#SBATCH --nodes=1
#SBATCH --time=24:00:00
#SBATCH --ntasks-per-node=16
#SBATCH --signal=B:SIGUSR1@1800

set INT=i8
module purge
module load gaussian16/A.03

# make a job tmpdir

mkdir ${TMPDIR}/${SLURM_JOB_NAME}
NEWTMP=${TMPDIR}/${SLURM_JOB_NAME}

export GAUSS_SCRDIR=${NEWTMP}

rsync -av --exclude 'slurm-*.out' ${SLURM_SUBMIT_DIR}/*.* $NEWTMP

cd $NEWTMP

((echo %rwf=${NEWTMP}/${SLURM_JOB_NAME}.rwf ; echo %NoSave; cat ${SLURM_JOB_NAME}.com ) | g16 2>&1 | tee ${SLURM_JOB_NAME}.log; rsync -av ${NEWTMP}/* ${SLURM_SUBMIT_DIR}/.; cd ${SLURM_SUBMIT_DIR}; rm -r $NEWTMP; echo "Ended normally") &

sid=($!)
trap "echo \"caught signal\"; kill ${sid[@]}; rsync -av $NEWTMP/* ${SLURM_SUBMIT_DIR}/.; rm -r $NEWTMP; echo \"ran out of time\"; exit 127" SIGUSR1


wait


