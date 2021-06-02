export PROJECT=${WORK2:-${HOME}/projects}/lccf
mkdir -p $PROJECT

# Establish build toolchain with default (Intel) modules.
CC=`which mpicc`
CXX=`which mpicxx`
export CC
export CXX
# In case cmake is available from several places later (such as from virtualenv),
# get the system CMake now.
CMAKE=`which cmake`
export CMAKE
