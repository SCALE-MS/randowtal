#!/bin/bash
# Build and install GROMACS 2021
# 2021 does not like the Intel compiler toolchain. Hopefully that's okay. We won't be actually using the Python bindings from the derived gmxapi package.
module load gcc
wget ftp://ftp.gromacs.org/gromacs/gromacs-2021.2.tar.gz
tar zxvf gromacs-2021.2.tar.gz
pushd gromacs-2021.2
  mkdir build
  pushd build
    cmake .. -DCMAKE_INSTALL_PREFIX=$PROJECT/gromacs2021 \
      -DCMAKE_C_COMPILER=`which gcc` \
      -DCMAKE_CXX_COMPILER=`which g++` \
      -DGMX_BUILD_OWN_FFTW=ON \
      -DGMX_THREAD_MPI=ON
    make -j10 install
  popd
popd
