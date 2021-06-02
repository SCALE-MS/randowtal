#!/bin/bash
. $ROOT/scripts/common.sh
. $PROJECT/py37/bin/activate
. $PROJECT/gromacs2019/bin/GMXRC

pushd $ROOT/external/brer_plugin
  mkdir build
  pushd build
    gmxapi_DIR=$PROJECT/gromacs2019/share/cmake/gmxapi \
    GROMACS_DIR=$PROJECT/gromacs2019/share/cmake/gromacs \
    $CMAKE ../ -DCMAKE_C_COMPILER=$CC -DCMAKE_CXX_COMPILER=$CXX \
      -DGMXPLUGIN_INSTALL_PATH=$PROJECT/py37/lib/python3.7/site-packages
    make -j10 install
  popd
popd