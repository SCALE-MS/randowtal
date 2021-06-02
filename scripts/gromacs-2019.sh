. $ROOT/scripts/common.sh

# Build and install GROMACS 2019
wget ftp://ftp.gromacs.org/pub/gromacs/gromacs-2019.6.tar.gz
tar zxvf gromacs-2019.6.tar.gz
pushd gromacs-2019.6
  mkdir build
  pushd build
    $CMAKE ../ \
      -DCMAKE_C_COMPILER=$CC \
      -DCMAKE_CXX_COMPILER=$CXX \
      -DCMAKE_INSTALL_PREFIX=$PROJECT/gromacs2019 \
      -DGMX_THREAD_MPI=ON \
      -DGMX_BUILD_OWN_FFTW=ON \
      -DGMXAPI=ON
    make -j10 install
  popd
popd
# I couldn't figure out what library would convince the GROMACS 2019 FindFFT.cmake script (Could not find fftwf_plan_many_[r2c|c2r])
#      -DFFTWF_LIBRARY=$MKLROOT/lib/intel64/libmkl_rt.so \
#      -DFFTWF_INCLUDE_DIR=$MKLROOT/include/fftw/ \
