#!/bin/bash

#PBS -V
#PBS -m bea
#PBS -M martin.peeks@chem.ox.ac.uk
#PBS -l walltime=99:00:00
#PBS -l nodes=1:ppn=16 
#PBS -l signal=3@1800
# that last command tells the schedular to send signal 3 to the script at 1800s before the end of the walltime. The script will catch this signal and will attempt to stop the job executable (orca) then move the gbw (wavefunction) file back to the shared disk

# here we ignore $TMPDIR from Torque, since it is on the network share so offers no performance benefit. Instead we will use the node's local /tmp.

# input name
INPUT=${PBS_JOBNAME}

# here will be our new tmp scratchspace
NEWTMP=/tmp/${PBS_JOBNAME}


# go to local scratch directory (see manual p. 27)
# if it already exists, delete it. otherwise make it and go there. (it = new scratch space)
rm -rf $NEWTMP
mkdir $NEWTMP
cd $NEWTMP


# copy input file to scratch
cp $PBS_O_WORKDIR/$INPUT.inp .

# prepare file with hostnames for (mpich-style) parallel run (see manual p. 28)
cp $PBS_NODEFILE $INPUT.nodes

# run orca, output redirected to *.out file on network share. Once complete, copy anything left in the scratch space back to the network share, and delete the network share. All of this is put into a subshell so that we can have the pid and kill it if we get signal 3.
($ORCA_PATH/orca $PWD/$INPUT.inp &> $PBS_O_WORKDIR/$INPUT.out; cp -u * $PBS_O_WORKDIR/; cd $PBS_O_WORKDIR; rm -r $NEWTMP; echo "Ended normally") & 

# get the pid of the job process
sid=($!)

# if we catch signal 3, then kill the job subshell and move the gbw file to the share. Then clean up /tmp.
trap "kill ${sid[@]};  mv $NEWTMP/*.gbw $PBS_O_WORKDIR; cd /tmp; rm -r $NEWTMP; echo \"ran out of time\"" 3


# remove hostname file
rm -f $INPUT.nodes

# this must be here otherwise the script would terminate with orca running in the background (&). Torque would then kill orca. 
wait
