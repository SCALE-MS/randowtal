
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

### Get access

1. Contact Matteo for an account on the VM at `95.217.193.116` to get a shell account and a MongoDB database.
1. Generate an ssh key pair (`ssh username@95.217.193.116 ssh-keygen`)
1. Ask Matteo/Andre to add the public key to `authorized_keys` for `rpilot@frontera.tacc.utexas.edu`.
1. Add `rpilot` to the Frontera allocation. Make sure that `rpilot@frontera` is a member of an appropriate group to get access to the software and data used by the scripts. *We're using group `G-821136`*
1. Let `rpilot` be the default user id when connecting from the VM to frontera. Add this to your ~/.ssh/config:
    ```
    host frontera.tacc.utexas.edu
       user = rpilot
    ```
    *Question: Why doesn't RP get this from the `rp.Context.user_id`?*

### Set up the client-side workflow environment.
Something like:
```
python3 -m pip ~/rp-venv
. ~/rp-venv/bin/activate; pip install --upgrade pip setuptools wheel
git clone git@github.com:SCALE-MS/scale-ms.git
pip install -r scale-ms/requirements-testing.txt
pip install -e scale-ms
git clone git@github.com:SCALE-MS/randowtal.git
```

### Set up the execution environment

On Frontera, the following assumes you did `export PROJECT=$HOME/projects/randowtal && mkdir -p $PROJECT` and that you are me.

git clone git@github.com:SCALE-MS/randowtal.git

... *tbd* ...

## Inputs

*tbd*

## Example

Originally, our lccf jobs used solely mpi4py ensemble management in gmxapi, exhibiting the following call hierarchy.

`job_normal.sh` -> `workflow.py` -> `import run_brer; ...`

We developed a RP-wrapped version of the workflow, architected as follows.

**Client side:** `clientdir/run_remote.sh` -> `rp-ensemble.py` -> `import radical.pilot as rp`

**Execution side:** rp.Task: `brer_runner.py` -> `import run_brer; ...`

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

* When creating a `rp.Context`, set `context.user_id = 'rpilot'`
* From the shell on the VM, start an ssh-agent, and add the key.
  `eval "$(ssh-agent -s)" && ssh-add ~/.ssh/id_rsa`
* Note the paths on the remote machine (frontera).
* Launch `tmux`! RP does not provide a way to disconnect the client from the Pilot session.
* Run the script to launch an rp Pilot as `rpilot@frontera`.

```shell      
export RADICAL_LOG_LVL=DEBUG
INPUT=/home1/02634/eirrgang/projects/lccf_gmx2021-patched/input/hiv-deer/nosugar_ver116.tpr
PAIRS=/home1/02634/eirrgang/projects/lccf_gmx2021-patched/input/hiv-deer/pair_dist.json
HOURS=0.5
SIZE=10
python ../rp-ensemble.py \
  --workers $SIZE \
  --threads 56 \
  --ensemble-size $SIZE \
  --resource frontera \
  --input $INPUT \
  --pairs $PAIRS \
  --walltime $HOURS \
  --workdir /scratch1/02634/eirrgang/brer-rp-gmx2019-$SIZE \
  --pre "module purge && module load intel/19.1.1 impi/19.0.9 git/2.24.1 autotools/1.2 python3/3.7.0 cmake/3.20.3 pmix/3.1.4 hwloc/1.11.12 xalt/2.10.13 TACC" \
  --pre ". /work2/02634/eirrgang/frontera/lccf/gromacs2019/bin/GMXRC" \
  --pre "umask 007" \
  --task /home1/02634/eirrgang/projects/lccf_rp/brer_runner.py \
  --python /work2/02634/eirrgang/frontera/lccf/py37/bin/python \
  --project MCB20024
```

