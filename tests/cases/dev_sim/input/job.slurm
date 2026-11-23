#!/bin/bash
#SBATCH --job-name=water_npt
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --time=24:00:00
#SBATCH --partition=cpu
module load lammps/2Aug2023
srun lmp -in in.npt -log log.lammps
