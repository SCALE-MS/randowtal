# Set up the software tools in $SCRATCH on Frontera.

# Requirements
module unload python3
module load gcc
module load python3

export PROJECT=${WORK2}/lccf-brer-gmx2021
mkdir -p $PROJECT

ROOT=$PWD
export ROOT

# Set up Python venv.
bash -x scripts/python-venv-default.sh

# Build and install GROMACS 2019
#bash -x scripts/gromacs-2019.sh

# Build and install gmxapi 0.0.7
#bash -x scripts/gmxapi-0.0.7.sh

# Build and install GROMACS 2021
bash -x scripts/gromacs-2021.sh

# Build and install brer_plugin
bash -x scripts/brer_plugin.sh

# Build and install Run-BRER
bash -x scripts/run_brer.sh

# Build and install gmxapi 0.2
bash -x scripts/gmxapi-0.2.sh
