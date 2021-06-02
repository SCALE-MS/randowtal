umask 027
export RADICAL_LOG_LVL=DEBUG
PROJECT=/work2/02634/eirrgang/frontera/lccf
. $PROJECT/py37/bin/activate
. $PROJECT/gromacs2019/bin/GMXRC
INPUT=/home1/02634/eirrgang/projects/lccf_gmx2021-patched/input/hiv-deer/nosugar_ver116.tpr
PAIRS=/home1/02634/eirrgang/projects/lccf_gmx2021-patched/input/hiv-deer/pair_dist.json
python /home1/02634/eirrgang/projects/lccf_rp/rp-ensemble.py --workers 2 --threads 8 --ensemble-size 2 --resource frontera --input $INPUT --pairs $PAIRS --walltime 1 --workdir . --gmxrc $PROJECT/gromacs2019/bin/GMXRC