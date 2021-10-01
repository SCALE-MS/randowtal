#!/usr/bin/env python3
# pylint: disable=redefined-outer-name

import os
import sys

import radical.utils as ru
import radical.pilot as rp

# This script has to run as a task within an pilot allocation, and is
# a demonstration of a task overlay within the RCT framework.
# It will:
#
#   - create a master which bootstraps a specific communication layer
#   - insert n workers into the pilot (again as a task)
#   - perform RPC handshake with those workers
#   - send RPC requests to the workers
#   - terminate the worker
#
# The worker itself is an external program which is not covered in this code.


# ------------------------------------------------------------------------------
#
class BrerMaster(rp.raptor.Master):
    '''
    This class provides the communication setup for the task overlay: it will
    set up the request / response communication queues and provide the endpoint
    information to be forwarded to the workers.
    '''

    # --------------------------------------------------------------------------
    #
    def __init__(self, cfg):

        rp.raptor.Master.__init__(self, cfg=cfg)

        self._workload = self._cfg.workload
        self._resource = self._cfg.resource
        self._config   = self._cfg.config

        cpw = int(self._resource.cores_per_node /
                  self._workload.workers_per_node)
        td  = rp.TaskDescription(self._resource.worker)
        td.named_env   = self._resource.named_env
        td.cpu_threads = cpw
        td.executable  = './brer_worker.py'
        td.sandbox     = os.getcwd()

        self._log.debug('=== start worker')
        self.submit(descr=td, count=self._workload.n_workers, cores=cpw, gpus=0)


    # --------------------------------------------------------------------------
    #
    def submit_tasks(self):

        self._prof.prof('submit_start')

        ensemble_size = self._workload.ensemble_size
        input         = self._workload.input
        pairs         = self._workload.pairs
        workdir       = self._cfg.workdir

        for idx in range(ensemble_size):

            for stage in ['training', 'convergence', 'production']:

                uid  = 'request.%s.%06d' % (stage, idx)
                item = {'uid'  :   uid,
                        'mode' :  'call',
                        'cores':  self._resource.cores_per_node,
                        'data' : {'method': stage,
                                  'kwargs': {'member' : idx,
                                             'workdir': workdir,
                                             'input'  : input,
                                             'pairs'  : pairs}}}
                self.request(item)

                # TODO: move output staging to master, needs stage_on_error
              # task_description.output_staging = [
              #     {
              #         'source': f'task:///{task_description.stdout}',
              #         'target': 'client:///',
              #         'action': rp.TRANSFER
              #     },
              #     {
              #         'source': f'task:///{task_description.stderr}',
              #         'target': 'client:///',
              #         'action': rp.TRANSFER
              #     },
              #     {
              #         'source': f'task:///brer{idx}.log',
              #         'target': f'client:///brer{self.ensemble_size}_mem_{member}.log',
              #         'action': rp.TRANSFER
              #     },
              # ]

        self._prof.prof('submit_stop')


    # --------------------------------------------------------------------------
    #
    def request_cb(self, requests):

        for req in requests:

            self._log.debug('=== request_cb %s\n' % (req['uid']))

        # return the original request for execution
        return requests


    # --------------------------------------------------------------------------
    #
    def result_cb(self, req):

        self._log.debug('=== result_cb  %s: %s [%s]\n'
                       % (req.uid, req.state, req.result))


# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    cfg    = ru.Config(cfg=ru.read_json(sys.argv[1]))
    master = BrerMaster(cfg)

    master.start()
    master.submit_tasks()
    master.join()
    master.stop()

    # FIXME: clean up workers


# ------------------------------------------------------------------------------

