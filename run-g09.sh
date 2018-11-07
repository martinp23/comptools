#!/bin/bash

if [ -x /opt/gridware/torque/latest/bin/qsub ]; then
	#PBS -V
	#PBS -l nodes=1
	#PBS -N $1
	#PBS -l walltime=$2
	#PBS -m bea
	#PBS -M martin.peeks@chem.ox.ac.uk


	cd $PBS_O_WORKDIR
	echo ${PBS_O_WORKDIR}
elif [ "$hostname" == "arcus-b" ]; then
	echo "pp"
else
	echo "bad host"
	exit 2
fi

(echo %rwf=${TMPDIR}/${1}.rwf ; echo %NoSave; cat ${1}.com ) | g09 > ${1}.log

