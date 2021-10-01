#!/usr/bin/env python3

import os
import sys

import radical.utils as ru
import radical.pilot as rp

from run_brer.run_config import RunConfig


# ------------------------------------------------------------------------------
#
class BrerWorker(rp.raptor.Worker):

    # --------------------------------------------------------------------------
    #
    def __init__(self, cfg):

        rp.raptor.Worker.__init__(self, cfg)


    # --------------------------------------------------------------------------
    #
    def training(self, count, uid):

        workload = self._cfg.workload


        os.umask(0o007)
        fast_run = {
            'tolerance'       : 10000,
            'num_samples'     : 2,
            'sample_period'   : 0.001,
            'production_time' : 10000.}
        config_params = {
            'tpr'             : os.path.abspath(args.input),
            'ensemble_num'    : args.member,
            'ensemble_dir'    : os.path.abspath(args.workdir),
            'pairs_json'      : os.path.abspath(args.pairs)
        }

        member_dir = os.path.join(os.path.abspath(args.workdir), f'mem_{args.member}')
        os.makedirs(member_dir, exist_ok=True)

        rc = RunConfig(**config_params)
        for key, value in fast_run.items():
            rc.run_data.set(**{key: value})
        if 'production_time' not in config_params:
            rc.run_data.set(production_time=100)  # sets production length to 100 ps
        rc.run_data.set(A=500)


def run_training(rc):
    # Training phase.
    assert rc.run_data.get('iteration') == 0
    if rc.run_data.get('phase') == 'training':
        rc.run(**run_kwargs)
        self._prof.prof('app_start', uid=uid)



# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    cfg    = ru.Config(cfg=ru.read_json(sys.argv[1]))
    worker = BrerWorker(sys.argv[1])
    worker.start()
    worker.join()


# ------------------------------------------------------------------------------





def run_convergence(rc):
    # Convergence phase.
    if rc.run_data.get('phase') == 'convergence':
        rc.run(**run_kwargs)


def run_production(rc):
    # Production phase.
    if rc.run_data.get('phase') == 'production':
        rc.run(**run_kwargs)


if __name__ == '__main__':

    rc = get_rc()
    run_training(rc)
    run_convergence(rc)
    run_production(rc)


