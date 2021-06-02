#!/bin/bash
#SBATCH -o brer.o%j       # Name of stdout output file
#SBATCH -e brer.e%j       # Name of stderr error file
#SBATCH -p normal          # Queue (partition) name
#SBATCH --cpus-per-task=56
#SBATCH -t 12:00:00        # Run time (hh:mm:ss)
#SBATCH --mail-type=all    # Send email at begin and end of job
#SBATCH -A MCB20006       # Project/Allocation name (req'd if you have more than 1)
#SBATCH --mail-user=ericirrgang@gmail.com

# See also https://frontera-portal.tacc.utexas.edu/user-guide/running/#table-5-frontera-production-queues

# Any other commands must follow all #SBATCH directives...

# Reference https://portal.tacc.utexas.edu/tutorials/managingio#python
#module load python_cacher
$PROJECT/py37/bin/python -m pip list
$PROJECT/py37/bin/python -c 'import run_brer; print("run_brer version:", run_brer.__version__)'

export PROJECT=${WORK2:-${HOME}/projects}/lccf
export ROOT=${HOME}/projects/lccf_adaptive
module list

umask 027
cp $ROOT/workflow.py $SCRATCH/
WORKDIR=$SCRATCH/brer-gmx2019-$SLURM_NTASKS
mkdir -p $WORKDIR
rsync -uav $ROOT/input/smFRET-tpr.tpr $WORKDIR/
rsync -uav $ROOT/input/pairs_loops.json $WORKDIR/
cd $WORKDIR || exit
pwd
ls
date

# Launch MPI code. Use ibrun instead of mpirun or mpiexec
. $PROJECT/gromacs2019/bin/GMXRC
ibrun $PROJECT/py37/bin/python -m mpi4py $SCRATCH/workflow.py \
        --input=$WORKDIR/smFRET-tpr.tpr \
        --ensemble-size=$SLURM_NTASKS \
        --workdir=$WORKDIR \
        --threads-per-sim=$SLURM_CPUS_PER_TASK \
        --pairs=$WORKDIR/pairs_loops.json
