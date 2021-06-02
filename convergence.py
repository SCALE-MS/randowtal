"""Run an ensemble of MD simulations across MPI ranks.

This is a run_brer script to manage one BRER ensemble member per MPI rank.

Usage:
    python -m mpi4py workflow.py <options>

For options, see ``python workflow.py --help``.

"""
import argparse
import logging
import os
import warnings
from typing import List

import mpi4py.MPI
import run_brer.run_config as rc

comm: mpi4py.MPI.Comm = mpi4py.MPI.COMM_WORLD
rank = comm.Get_rank()

logger = logging.getLogger()
# Logging
# logger.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter(f'%(asctime)s:%(name)s[{rank}]:%(levelname)s - %(message)s')
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(ch)


class BrerEnsemble:
    """Runnable BRER ensemble task.

    Arguments:
        input: TPR file list to start from
        dir: Base directory for the ensemble
        pairs: JSON file containing pairs data
        threads: Number of threads each simulation should restrict itself to (optional).

    """
    def __init__(self,
                 input: List[str],
                 dir: str,
                 pairs: str,
                 threads: int = None):
        run_config = rc.RunConfig(
            tpr=input,
            ensemble_dir=dir,
            pairs_json=pairs
        )
        run_config.run_data.set(production_time=50000)  # sets production length to 50 ns
        run_config.run_data.set(A=500)
        self.run_config = run_config
        self.threads = threads

    def run(self):
        if self.run_config.run_data.get('iteration') != 0:
            warnings.warn('BRER production run has finished for this member.')
        while self.run_config.run_data.get('phase') != 'production':
            phase = self.run_config.run_data.get('phase')
            logger.info(f'Launching simulation for {phase} phase.')
            kwargs = {}
            if self.threads is not None:
                kwargs['threads'] = self.threads
            self.run_config.run(**kwargs)


parser = argparse.ArgumentParser()
parser.add_argument(
    '--ensemble-size',
    type=int,
    help='Number of members in the ensemble (to run one simulation per rank.')
parser.add_argument(
    '--threads-per-sim',
    type=int,
    help='Simulation threads per Python process (MPI rank).'
)
parser.add_argument(
    '--input',
    type=str,
    help='Common input TPR file from which to initialize simulations.'
)
parser.add_argument(
    '--pairs',
    type=str,
    help='JSON file containing molecular site pair data'
)
parser.add_argument(
    '--workdir',
    type=str,
    help='Base directory for the BRER ensemble'
)

if __name__ == '__main__':
    args = parser.parse_args()
    N = args.ensemble_size

    assert os.path.exists(args.input)
    assert os.path.exists(args.pairs)
    assert os.path.exists(args.workdir)

    input_list = [args.input] * N
    ensemble_task = BrerEnsemble(
        input=input_list,
        dir=args.workdir,
        pairs=args.pairs,
        threads=args.threads_per_sim
    )
    ensemble_task.run()
