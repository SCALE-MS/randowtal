"""Executable for BRER tasks.

This script provides the executable for RADICAL Pilot Tasks launched by rp-ensemble.py.
"""
import argparse
import os

from run_brer.run_config import RunConfig


parser = argparse.ArgumentParser()
parser.add_argument(
    '--member',
    type=int,
    required=True,
    help="Index of this task in the BRER ensemble."
)
# TODO: We could add a workaround for more deterministic interruption and force error
#  conditions.
# parser.add_argument(
#     '--walltime',
#     type=float,
#     help="Wall time (in hours)"
# )
parser.add_argument(
    '--input',
    type=str,
    required=True,
    help='Common input TPR file from which to initialize simulations.'
)
parser.add_argument(
    '--pairs',
    type=str,
    required=True,
    help='JSON file containing molecular site pair data.'
)
parser.add_argument(
    '--workdir',
    type=str,
    required=True,
    help='Base directory for the BRER ensemble.'
)
# Task does not have access to its own TaskDescription at run time.
parser.add_argument(
    '--threads',
    type=int,
    help='(Optional) Number of CPUs to use for this BRER simulation.'
)
args = parser.parse_args()


if __name__ == '__main__':
    os.umask(0o007)
    fast_run = {
        'tolerance': 10000,
        'num_samples': 2,
        'sample_period': 0.001,
        'production_time': 10000.}
    config_params = {
        'tpr': os.path.abspath(args.input),
        'ensemble_num': args.member,
        'ensemble_dir': os.path.abspath(args.workdir),
        'pairs_json': os.path.abspath(args.pairs)
    }
    config_params.update(fast_run)

    member_dir = os.path.join(os.path.abspath(args.workdir), f'mem_{args.member}')
    os.makedirs(member_dir, exist_ok=True)

    run_kwargs = {}
    if args.threads:
        run_kwargs['threads'] = args.threads

    rc = RunConfig(**config_params)
    rc.run_data.set(production_time=100)  # sets production length to 100 ps
    rc.run_data.set(A=500)

    # Training phase.
    assert rc.run_data.get('iteration') == 0
    assert rc.run_data.get('phase') == 'training'

    rc.run(**run_kwargs)

    # Convergence phase.
    assert rc.run_data.get('phase') == 'convergence'
    rc.run(**run_kwargs)

    # Production phase.
    assert rc.run_data.get('phase') == 'production'
    rc.run(**run_kwargs)
