# Set up Python venv using default (3.7) interpreter.
VENV=$PROJECT/py38-gmx2021
export VENV

. $ROOT/scripts/common.sh
python3 -m venv $VENV
. $VENV/bin/activate
pip install --upgrade --no-build-isolation pip setuptools wheel
pip install --upgrade --no-build-isolation scikit-build
MPICC=`which mpicc` pip install mpi4py
