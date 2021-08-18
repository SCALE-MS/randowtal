#ROOT=${ROOT:-$HOME/projects/lccf_adaptive}
#export ROOT
if [ -z "$ROOT" ]; then
  echo "ERROR: Need to set ROOT to the local repository dir."
else

export PROJECT=${WORK2}/lccf-brer-gmx2021
mkdir -p $PROJECT

VENV=$PROJECT/py38-gmx2021
export VENV

# In case cmake is available from several places later (such as from virtualenv),
# get the system CMake now.
CMAKE=`which cmake`
export CMAKE

module unload python3
module load gcc
module load python3

# Establish build toolchain with default (Intel) modules.
CC=`which mpicc`
CXX=`which mpicxx`
export CC
export CXX
. $VENV/bin/activate
. $PROJECT/gromacs2021/bin/GMXRC

fi

