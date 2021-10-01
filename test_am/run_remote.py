#!/usr/bin/env python3

import json

import radical.pilot as rp
import radical.utils as ru


BASE    = "/home1/02634/eirrgang/"
SCRATCH = "/scratch1/02634/eirrgang/"
DATA    = "%s/projects/lccf_gmx2021-patched/input/hiv-deer/" % BASE
INPUT   = "%s/nosugar_ver116.tpr" % DATA
PAIRS   = "%s/pair_dist.json" % DATA
HOURS   = 0.5
SIZE    = '2'
GMX_LOC = '/work/02634/eirrgang/frontera/software/gromacs2021'


# ------------------------------------------------------------------------------
workload  = {
             'ensemble_size'   : int(SIZE),
             'input'           : INPUT,
             'pairs'           : PAIRS,
             'n_workers'       : int(SIZE),
             'workers_per_node': 1
            }

config    = {
             'resource'        : 'localhost',
             'walltime'        : HOURS,
             'workdir'         : SCRATCH + '/randowtal/brer-rp-gmx2021-' + SIZE,
            }

resources = {'frontera' : {
                 'cores_per_node': 56,
                 'pilot' : {'resource'      : 'tacc.frontera',
                            'access_schema' : 'ssh',
                            'project'       : 'MCB20024',
                            'queue'         : 'development',
                           },
                 'master': {'pre_exec': ['umask 007',
                                         'module unload python3',
                                         'module unload impi',
                                         'module unload intel',
                                         'module load   gcc',
                                         'module load   impi',
                                         'module load   python3',
                                         '. %s/bin/GMXRC' % GMX_LOC,
                                         ]},
                 'worker': {'pre_exec': ['umask 007',
                                         'module unload python3',
                                         'module unload impi',
                                         'module unload intel',
                                         'module load   gcc',
                                         'module load   impi',
                                         'module load   python3',
                                         '. %s/bin/GMXRC' % GMX_LOC,
                                         ]}},
             'localhost': {
                 'cores_per_node': 4,
                 'pilot' : {'resource'      : 'local.localhost',
                            'access_schema' : 'ssh'},
                 'master': {},
                 'worker': {}}
             }


# ------------------------------------------------------------------------------
#
class RunTime:
    """Configure and manage the runtime environment."""

    # --------------------------------------------------------------------------
    def __init__(self, cfg) -> None:

        self._cfg     = ru.Config(cfg=cfg)
        self._session = None
        self._pmgr    = None
        self._tmgr    = None
        self._master  = None
        self._pilot   = None

        self._log     = ru.Logger('brer.runner', level='DEBUG',
                                                 targets=['.', '-'])

        self._resource_label = cfg.get('resource', 'localhost')
        self._resource       = ru.Config(cfg=resources[self._resource_label])


    # --------------------------------------------------------------------------
    #
    def __del__(self) -> None:

        self.stop()


    # --------------------------------------------------------------------------
    #
    def stop(self) -> None:

        if self._session:
            try   : self._session.close(download=True)
            except: pass
            self._session = None


    # --------------------------------------------------------------------------
    #
    def _pilot_state_cb(self, pilot, state):

        if not self._pilot:
            self._log.debug('early state update for %s: %s',
                            pilot.uid, pilot.state)
            return

        assert(pilot.uid == self._pilot.uid)
        self._log.debug('state update for %s: %s', pilot.uid, pilot.state)

        if pilot.state == rp.FAILED:
            self._log.error('run context failed - abort')
            self.stop()

        elif pilot.state == rp.CANCELED:
            self._log.error('run context canceled - abort')
            self.stop()

        elif pilot.state == rp.DONE:
            self._log.error('run context completed')
            self.stop()


    # --------------------------------------------------------------------------
    #
    def _task_state_cb(self, task, state):

        if not self._master:
            self._log.debug('early state update for %s: %s',
                            task.uid, task.state)
            return

        assert(task.uid == self._master.uid)
        self._log.debug('state update for %s: %s', task.uid, task.state)

        if task.state == rp.FAILED:
            self._log.error('workload failed - abort')
            self.stop()

        elif task.state == rp.CANCELED:
            self._log.error('workload canceled - abort')
            self.stop()

        elif task.state == rp.DONE:
            self._log.error('workload completed')
            self.stop()


    # --------------------------------------------------------------------------
    #
    def start(self, n_workers: int, workers_per_node: int) -> None:

        assert(not self._session)

        self._session = rp.Session()
        self._pmgr    = rp.PilotManager(self._session)
        self._tmgr    = rp.TaskManager(self._session)

        self._pmgr.register_callback(self._pilot_state_cb)
        self._tmgr.register_callback(self._task_state_cb)

        if self._resource_label == 'frontera':
            context = rp.Context('ssh')
            context.user_id = 'rpilot'
            self._session.add_context(context)

        pd = rp.PilotDescription(from_dict=self._resource.pilot)

        # number of cores for the workers plus one node for the master
        cpn      = int(self._resource.cores_per_node)
        pd.cores = n_workers / workers_per_node * cpn + cpn

        self._pilot = self._pmgr.submit_pilots(pd)
        self._tmgr.add_pilots(self._pilot)

        modules = [
                'git+https://github.com/SCALE-MS/scale-ms.git@master',
                'git+https://github.com/SCALE-MS/run_brer.git@master',
                'git+https://github.com/radical-cybertools/radical.pilot.git'
                         + '@project/scalems',
              # 'gmxapi'
        ]
        pre_exec = self._resource.master.pre_exec

        # NOTE: this will block until pilot is alive and venv exists
        # TODO: pre_exec
        self._pilot.prepare_env(env_name='ve_brer',
                                env_spec={'type'    : 'virtualenv',
                                          'version' : '3.8',
                                          'pre_exec': pre_exec,
                                          'setup'   : modules})

        self._resource.named_env = 've_brer'


    # --------------------------------------------------------------------------
    #
    def submit_workload(self, workload):

        workload = ru.Config(cfg=workload)

        self.start(workload.n_workers, workload.workers_per_node)

        master_cfg = {
                'workload': workload,
                'resource': self._resource,
                'config'  : self._cfg}
        ru.write_json(master_cfg, './config.json')

        # TODO: stage input data
        td = rp.TaskDescription(self._resource.master)
        td.uid            = 'brer_master'
        td.named_env      = self._resource.named_env
        td.executable     = './brer_master.py'
        td.cpu_threads    = self._resource.cores_per_node
        td.arguments      = ['config.json']
        td.input_staging  = ['brer_master.py',
                             'brer_worker.py',
                             'config.json']

        self._master = self._tmgr.submit_tasks(td)
        self._master.wait(state=[rp.AGENT_EXECUTING])

        td = rp.TaskDescription()
        td.uid            = 'brer_workload'
        td.named_env      = self._resource.named_env
        td.executable     = '-'
        td.scheduler      = 'brer_master'
        td.cpu_threads    = self._resource.cores_per_node
        td.arguments      = [json.dumps(workload.as_dict())]
        self._work = self._tmgr.submit_tasks(td)

        self._tmgr.wait_tasks()


# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    rc = None
    try:
        rc = RunTime(cfg=config)
        rc.submit_workload(workload)

    finally:
        if rc: rc.stop()

# ------------------------------------------------------------------------------

