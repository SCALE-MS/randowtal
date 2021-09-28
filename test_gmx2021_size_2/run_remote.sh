export RADICAL_LOG_LVL=DEBUG
INPUT=/home1/02634/eirrgang/projects/lccf_gmx2021-patched/input/hiv-deer/nosugar_ver116.tpr
PAIRS=/home1/02634/eirrgang/projects/lccf_gmx2021-patched/input/hiv-deer/pair_dist.json
HOURS=0.5
SIZE=2
python ../rp-ensemble.py \
  --workers $SIZE \
  --threads 56 \
  --ensemble-size $SIZE \
  --resource frontera \
  --input $INPUT \
  --pairs $PAIRS \
  --walltime $HOURS \
  --workdir /scratch1/02634/eirrgang/randowtal/brer-rp-gmx2021-$SIZE \
  --pre ". /home1/02634/eirrgang/projects/randowtal/modules.frontera" \
  --pre "umask 007" \
  --task /home1/02634/eirrgang/projects/randowtal/brer_runner.py \
  --python /work/02634/eirrgang/frontera/venv/randowtal/bin/python \
  --project MCB20024 \
  --queue development
