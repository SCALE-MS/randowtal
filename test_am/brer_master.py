#!/usr/bin/env python3

import os
import sys
import copy
import json

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

        self._dependencies = dict()
        self._submitted    = 0
        self._completed    = 0
        self._workloads    = list()

        self._log.debug('=== start worker')
        self.submit(descr=td, count=self._workload.n_workers, cores=cpw, gpus=0)


    # --------------------------------------------------------------------------
    #
    def request_cb(self, requests):

        for req in requests:

            args     = req['task']['description']['arguments']
            workload = ru.Config(cfg=json.loads(args[0]))

            self._log.debug('=== request_cb %s\n' % (req['uid']))

            ensemble_size = workload.ensemble_size
            input         = workload.input
            pairs         = workload.pairs
            workdir       = self._cfg.config.workdir

            for idx in range(ensemble_size):

                uid  = 'request.%06d' % idx
                item = {'uid'  :  uid,
                        'mode' :  'call',
                        'cores':  self._resource.cores_per_node,
                        'data' : {'method': 'brer_run',
                                  'kwargs': {'stage'  : 'training',
                                             'member' : idx,
                                             'workdir': workdir,
                                             'input'  : input,
                                             'pairs'  : pairs}}}

                req_training    = copy.deepcopy(item)
                req_convergence = copy.deepcopy(item)
                req_production  = copy.deepcopy(item)

                req_training['uid']    = uid + '.training'
                req_convergence['uid'] = uid + '.convergence'
                req_production['uid']  = uid + '.production'

                req_training['data']['kwargs']['stage']    = 'training'
                req_convergence['data']['kwargs']['stage'] = 'convergence'
                req_production['data']['kwargs']['stage']  = 'production'

                self._dependencies[req_training['uid']]    = req_convergence
                self._dependencies[req_convergence['uid']] = req_production

                self._log.debug('=== submit task %s\n', req_training['uid'])
                self.request(req_training)
                self._submitted += 1

                self._workloads.append(req)


    # --------------------------------------------------------------------------
    #
    def result_cb(self, req):

        self._log.debug('=== result_cb  %s: %s [%s]',
                        req.uid, req.state, req.result)
        self._completed += 1

        if req.uid in self._dependencies:
            dep = self._dependencies[req.uid]
            self._log.debug('=== submit dep  %s', dep['uid'])
            self.request(dep)
            self._submitted += 1

        if self._submitted == self._completed:
            # we are done, not more workloads to wait for - return the tasks
            # and terminate
            for req in self._workloads:
                req['task']['target_state'] = rp.DONE
                self.advance(req['task'], rp.AGENT_STAGING_OUTPUT_PENDING,
                                       publish=True, push=True)

            self.stop()


# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    cfg    = ru.Config(cfg=ru.read_json(sys.argv[1]))
    master = BrerMaster(cfg)

    master.start()
    master.join()
    master.stop()


# ------------------------------------------------------------------------------

