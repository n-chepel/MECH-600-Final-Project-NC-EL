#!/bin/bash
#SBATCH --account=def-sponsor00     # your course allocation
#SBATCH --job-name=edmtest      # a name you will recognise in the queue
#SBATCH --time=08:00:00         # walltime HH:MM:SS
#SBATCH --ntasks=4              # 4 MPI ranks  ==  4 subdomains
#SBATCH --mem=8G        # memory per rank
#SBATCH --output=%x-%j.out      # log file named <job-name>-<jobid>.out



module load openfoam/v2412      # make the OpenFOAM commands available

mpirun -np $SLURM_NTASKS simpleFoam -parallel    # run the solver across the 8 ranks
reconstructPar -latestTime      # merge the final result back into one case