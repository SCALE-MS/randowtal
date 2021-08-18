. $ROOT/scripts/common.sh
. $PROJECT/gromacs2019/bin/GMXRC

wget https://github.com/kassonlab/gmxapi/archive/release-0_0_7.tar.gz
tar zxvf release-0_0_7.tar.gz
pushd gmxapi-release-0_0_7
  pip install -r requirements.txt
  mkdir build
  pushd build
    gmxapi_DIR=$PROJECT/gromacs2019/share/cmake/gmxapi \
    $CMAKE ../ -DCMAKE_C_COMPILER=$CC -DCMAKE_CXX_COMPILER=$CXX \
      -DGMXAPI_INSTALL_PATH=$VENV/lib/python3.7/site-packages/gmx
    make -j10 install
  popd
popd
