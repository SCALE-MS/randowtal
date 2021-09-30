export RADICAL_LOG_LVL=DEBUG
BASE=/home1/02634/eirrgang/
SCRATCH=/scratch1/02634/eirrgang/
INPUT=$BASE/projects/lccf_gmx2021-patched/input/hiv-deer/nosugar_ver116.tpr
PAIRS=$BASE/projects/lccf_gmx2021-patched/input/hiv-deer/pair_dist.json
HOURS=0.5
SIZE=2
python3 ../rp-ensemble.py \
  --workers $SIZE \
  --threads 56 \
  --ensemble-size $SIZE \
  --resource frontera \
  --input $INPUT \
  --pairs $PAIRS \
  --walltime $HOURS \
  --workdir $SCRATCH/randowtal/brer-rp-gmx2021-$SIZE \
  --pre "umask 007" \
  --pre "module unload python3" \
  --pre "module unload impi" \
  --pre "module unload intel" \
  --pre "module load gcc" \
  --pre "module load impi" \
  --pre "module load python3" \
  --task brer_runner.py \
  --project MCB20024 \
  --queue development

# --python /work/02634/eirrgang/frontera/venv/randowtal/bin/python \
# Note that this does not do anything to confirm the remote package versions.
