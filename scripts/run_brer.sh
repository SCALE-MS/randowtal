#!/bin/bash
. $ROOT/scripts/common.sh
. $PROJECT/py37/bin/activate
. $PROJECT/gromacs2019/bin/GMXRC

pushd $ROOT/external/run_brer
  # Use setup.py instead of pip as a quick way to avoid automatic network access...
  python setup.py install
popd