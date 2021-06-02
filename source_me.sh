export PROJECT=${WORK2:-${HOME}/projects}/lccf
ROOT=$HOME/projects/lccf_adaptive
export ROOT

# In case cmake is available from several places later (such as from virtualenv),
# get the system CMake now.
CMAKE=`which cmake`
export CMAKE

# Establish build toolchain with default (Intel) modules.
CC=`which mpicc`
CXX=`which mpicxx`
export CC
export CXX
. $PROJECT/py37/bin/activate
. $PROJECT/gromacs2019/bin/GMXRC
