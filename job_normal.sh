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

. modules.frontera
. $WORK/venv/randowtal/bin/activate
pip list
python -c 'import run_brer; print("run_brer version:", run_brer.__version__)'

module list

if [ -z "$ROOT" ]; then
  echo "Need to set ROOT to the local repository dir."
  exit 1
fi

umask 027
cp $ROOT/workflow.py $SCRATCH/
WORKDIR=$SCRATCH/brer-gmx2021-$SLURM_NTASKS
mkdir -p $WORKDIR
rsync -uav $ROOT/input/hiv-deer/nosugar_ver116.tpr $WORKDIR/
rsync -uav $ROOT/input/hiv-deer/pair_dist.json $WORKDIR/
cd $WORKDIR || exit
pwd
ls
date

# Launch MPI code. Use ibrun instead of mpirun or mpiexec
. $PROJECT/gromacs2021/bin/GMXRC
ibrun $VENV/bin/python -m mpi4py $SCRATCH/workflow.py \
        --input=$WORKDIR/nosugar_ver116.tpr \
        --ensemble-size=$SLURM_NTASKS \
        --workdir=$WORKDIR \
        --threads-per-sim=$SLURM_CPUS_PER_TASK \
        --pairs=$WORKDIR/pair_dist.json
