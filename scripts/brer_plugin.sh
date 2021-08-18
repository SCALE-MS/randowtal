#!/bin/bash
. $ROOT/scripts/common.sh
. $VENV/bin/activate
. $PROJECT/gromacs2021/bin/GMXRC

pushd $ROOT/external/brer_plugin
  mkdir build
  pushd build
    gmxapi_DIR=$PROJECT/gromacs2021/share/cmake/gmxapi \
    GROMACS_DIR=$PROJECT/gromacs2021/share/cmake/gromacs \
    $CMAKE ../ -DCMAKE_C_COMPILER=$CC -DCMAKE_CXX_COMPILER=$CXX \
      -DGMXPLUGIN_INSTALL_PATH=$VENV/lib/python3.8/site-packages
    make -j10 install
  popd
popd
