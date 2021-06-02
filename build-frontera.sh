# Set up the software tools in $SCRATCH on Frontera.

# Requirements
#module unload
#module load
# Default modules seem fine:   1) intel/19.1.1   2) impi/19.0.9   3) git/2.24.1   4) autotools/1.2   5) python3/3.7.0   6) cmake/3.16.1   7) pmix/3.1.4   8) hwloc/1.11.12   9) xalt/2.10.2  10) TACC

export PROJECT=${WORK2:-${HOME}/projects}/lccf
mkdir -p $PROJECT

ROOT=$PWD
export ROOT

# Set up Python venv.
bash -x scripts/python-venv-default.sh

# Build and install GROMACS 2019
bash -x scripts/gromacs-2019.sh

# Build and install gmxapi 0.0.7
bash -x scripts/gmxapi-0.0.7.sh

# Build and install brer_plugin
bash -x scripts/brer_plugin.sh

# Build and install Run-BRER
bash -x scripts/run_brer.sh

# Build and install GROMACS 2021
bash -x scripts/gromacs-2021.sh

# Build and install gmxapi 0.2
bash -x scripts/gmxapi-0.2.sh
