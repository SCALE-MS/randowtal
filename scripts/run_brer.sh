#!/bin/bash
. $ROOT/scripts/common.sh
. $VENV/bin/activate
. $PROJECT/gromacs2021/bin/GMXRC

pushd $ROOT/external/run_brer
  # Use setup.py instead of pip as a quick way to avoid automatic network access...
  python setup.py install
popd