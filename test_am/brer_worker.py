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
    def brer_run(self, stage  : str,
                       member : int,
                       workdir: str,
                       input  : str,
                       pairs  : str) -> str:

        uid = os.environ['RP_TASK_ID']
        self._prof.prof('app_%s_start' % stage, uid=uid)

        os.umask(0o007)
        fast_run = {
            'tolerance'       : 10000,
            'num_samples'     : 2,
            'sample_period'   : 0.001,
            'production_time' : 10000.}
        config_params = {
            'tpr'             : os.path.abspath(input),
            'ensemble_num'    : member,
            'ensemble_dir'    : os.path.abspath(workdir),
            'pairs_json'      : os.path.abspath(pairs)
        }

        member_dir = os.path.join(os.path.abspath(workdir), f'mem_{member}')
        os.makedirs(member_dir, exist_ok=True)

        rc = RunConfig(**config_params)
        for key, value in fast_run.items():
            rc.run_data.set(**{key: value})
        if 'production_time' not in config_params:
            rc.run_data.set(production_time=1)  # production length: 100 ps
        rc.run_data.set(A=500)
        rc.run(threads=self._cfg.resource.cores_per_node)

        self._prof.prof('app_%s_stop' % stage, uid=uid)


# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    cfg    = ru.Config(cfg=ru.read_json(sys.argv[1]))
    worker = BrerWorker(sys.argv[1])
    worker.start()
    worker.join()


# ------------------------------------------------------------------------------

