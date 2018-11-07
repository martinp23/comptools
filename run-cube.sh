#!/bin/bash

#SBATCH --nodes=1
#SBATCH --time=0:10:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=martin.peeks@chem.ox.ac.uk
#SBATCH --ntasks-per-node=16

GAUSS_MEMDEF=10GB cubegen 16 spin=scf mpc100-wpbe-1.fchk mpc100-wpbe-1.cube -3

