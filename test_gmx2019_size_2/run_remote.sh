export RADICAL_LOG_LVL=DEBUG
INPUT=/home1/02634/eirrgang/projects/lccf_gmx2021-patched/input/hiv-deer/nosugar_ver116.tpr
PAIRS=/home1/02634/eirrgang/projects/lccf_gmx2021-patched/input/hiv-deer/pair_dist.json
HOURS=1
SIZE=2
python ../rp-ensemble.py \
  --workers 2 \
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
