
Clone with `git clone --recursive git@github.com:scalems/randowtal.git`

Update with `git pull --recurse-submodules`

## Contents

Assume the repository is cloned to `$PROJECT`.

`$PROJECT`/ contains some bash SLURM scripts and some Python workflow scripts.

Additionally, `build-frontera.sh` prepares the complete project environment, using supporting scripts in `$PROJECT/scripts`.

`$PROJECT/input` contains some GROMACS and BRER input files.

`$PROJECT/external` contains some `git` submodules.

Additional files and directories may be created in the repository by jobs or scripts, but most storage will target `$WORK2` or `$SCRATCH`.

`git` submodules include
* `run_brer` Python package
* BRER plugin for GROMACS MD (`brer` Python package)

The build also requires downloads of archives for
* GROMACS 2021 (supporting gmxapi 0.2)
* gmxapi 0.2 (via pip)

## Set up

At least one Python `venv` and at least one GROMACS installation are needed.

`build-frontera.sh` should just work, but should also be fairly self-explanatory on inspection.

## Inputs

Inputs include a TPR file and a JSON file (pairs data). Sources are stashed in the `input` directory.

The TPR file is generated with

    cd input
    . $PROJECT/gromacs2021/bin/GMXRC  # See build-frontera.sh
    gmx grompp -f smfret-md-params.mdp -c step5_production.gro -p loops-topol.top -o smFRET-tpr.tpr

## Example

### mpi4py gmxapi ensemble management
Assuming
* `$ROOT` is the base of this repo
* the project has been set up as per `build-frontera.sh`
* `N` is the number of MPI ranks (one per node)
* `n` is the number of threads per simulation (cores per node)

    mkdir $SCRATCH/brer-test-N
    $PROJECT/py37/bin/python -m mpi4py $ROOT/workflow.py \
        --input=$ROOT/input/smFRET-tpr.tpr \
        --ensemble-size=N \
        --workdir=$SCRATCH/brer-test-N \
        --threads-per-sim=n \
        --pairs=pairs_loops.json

The above example is wrapped by `job_normal.sh`, which requires missing sbatch options to be provided on the command line.
Example:

    for N in 1 4 16 64 128 256; do sbatch -J brer2019_$N -N $N -n $N job_normal.sh ; done

### RADICAL Pilot ensemble management

`rp-ensemble.py` is used to launch `brer_runner.py`.

See https://github.com/kassonlab/lccf_adaptive/wiki/RADICAL-Pilot#frontera-execution for more detail.
