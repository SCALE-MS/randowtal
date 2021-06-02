# Set up Python venv using default (3.7) interpreter.
python3 -m venv $PROJECT/py37
. $PROJECT/py37/bin/activate
pip install --upgrade --no-build-isolation pip setuptools wheel
pip install --upgrade --no-build-isolation scikit-build
# Frontera already has mpi4py for impi19
#MPICC=`which mpicc` pip install mpi4py
pip install mpi4py
