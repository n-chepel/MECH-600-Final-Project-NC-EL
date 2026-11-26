#!/bin/bash
#SBATCH --account=def-sponsor00     # your course allocation
#SBATCH --job-name=edmtest      # a name you will recognise in the queue
#SBATCH --time=08:00:00         # walltime HH:MM:SS
#SBATCH --ntasks=4              # 4 MPI ranks  ==  4 subdomains
#SBATCH --mem=8G        # memory per rank
#SBATCH --output=%x-%j.out      # log file named <job-name>-<jobid>.out

python3 generate_ahmed_body.py

module load openfoam/v2412      # make the OpenFOAM commands available

blockMesh
surfaceFeatureExtract
decomposePar -force             # split the case into processor0/ ... processor7/

mpirun -np $SLURM_NTASKS snappyHexMesh -overwrite -parallel       
reconstructParMesh -constant    
rm -rf processor*
checkMesh
decomposePar -force             # divide into precessors

mpirun -np $SLURM_NTASKS simpleFoam -parallel    # run the solver across the 8 ranks
reconstructPar -latestTime      # merge the final result back into one case