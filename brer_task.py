"""Configure and run MD with BRER extension.

Based on a job script from caroline davis (cnd7cy): hiv env trimer

Warning: The ability to continue trajectories depends on the domain decomposition
geometry. If the number of PP or PME ranks changes, new TPR files need to be created
manually.
"""
""" run script for BRER simulations
 :param: tpr file: topology of the system
 :param: ensemble_directory: path to ensemble
 :param: ensemble_num: identifies which ensembles members will run; int value
 :param: pairs_json: contains specified residues pairs that brer will use; json file
"""
import os

import gmxapi as gmx
import run_brer.run_config as rc


scratch = os.getenv('SCRATCH')
home = os.getenv('HOME')
assert os.path.exists(scratch)
assert scratch != ''


def get_config(*, member: int, input: str, dir: str, pairs: str) -> rc.RunConfig:
    """Get the runnable.

    Arguments:
        member: Ensemble member ID
        input: TPR file to start from
        dir: Base directory for the ensemble
        pairs: JSON file containing pairs data

    Returns:
        run_brer RunConfig instance.
    """
    init = {
        'tpr': os.path.join(home, 'smFRET-tpr.tpr'),
        'ensemble_dir': os.path.join(scratch, 'hiv-smfret-brer'),
        'ensemble_num': member,
        'pairs_json': os.path.join(scratch, 'hiv-smfret-brer/pairs_loops.json')
    }
    config = rc.RunConfig(**init)  # allows for the dictionary/"constructor" to be used as a parameter
    config.run_data.set(production_time=50000)  # sets production length to 50 ns
    config.run_data.set(A=500)  # sets energy constant to 100 kcal/mol/nm^2
    return config


# checks for corrupt or missing tpr file in production phase
#newTPR = os.path.join(scratch, 'hiv-smfret-brer', str(args.member), '0/convergence/new-loop-tpr.tpr')

#if os.path.exists(newTPR) and rc.run_data.get('phase') == 'production':  # check to see if the mem_ has a new tpr and in production phase
	#thisfile = newTPR
#else:
	#thisfile = None

# gives optimal thread count
# ncores = int(os.getenv('SLURM_JOB_CPUS_PER_NODE'))

@gmx.function_wrapper(output={'phase': str})
def run_brer(output):
    config = get_config(

    )
    config.run()
    output.phase = config.run_data.get('phase')