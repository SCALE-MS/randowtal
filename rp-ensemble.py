"""RADICAL Pilot job script for ensemble of BRER simulations.

RP scripts are executed _instead of_ a SLURM job script and take care of
job submission on behalf of the user.

This script manages a RADICAL Pilot session for submitting tasks based on the
`brer_runner.py` executable script.
"""

import argparse
import contextlib
import functools
import os
import pathlib
import sys
import typing
import warnings

import radical.pilot as rp

parser = argparse.ArgumentParser()
parser.add_argument(
    '--workers',
    metavar='N',
    type=int,
    default=1,
    help="Number of workers to use."
)
parser.add_argument(
    '--threads',
    metavar='NUM_THREADS',
    type=int,
    help='(Optional) Number of CPUs to use for each BRER simulation. (Default: auto)'
)
parser.add_argument(
    '--ensemble-size',
    metavar='M',
    type=int,
    required=True,
    help="Number of BRER ensemble members"
)
parser.add_argument(
    '--resource',
    choices=('frontera', 'localhost'),
    required=True,
    help='Targeted resource.'
)
parser.add_argument(
    '--walltime',
    metavar='HOURS',
    type=float,
    required=True,
    help="Wall time (in hours)"
)
parser.add_argument(
    '--input',
    metavar='TPRFILE',
    type=str,
    required=True,
    help='Common input TPR file from which to initialize simulations.'
)
parser.add_argument(
    '--pairs',
    metavar='JSONFILE',
    type=str,
    required=True,
    help='JSON file containing molecular site pair data'
)
parser.add_argument(
    '--workdir',
    type=str,
    required=True,
    help='Base directory for the BRER ensemble'
)
parser.add_argument(
    '--task',
    metavar='SCRIPT',
    type=pathlib.Path,
    default=pathlib.Path(__file__).parent / 'brer_runner.py',
    help='Executable task to launch with RP.'
)
parser.add_argument(
    '--pre',
    action='append',
    help='Append shell expressions to the pre_exec list. (optional)'
)
parser.add_argument(
    '--project',
    type=str,
    default='MCB20006',
    help='Allocation under which RP should submit jobs on Frontera.'
)
parser.add_argument(
    '--queue',
    type=str,
    default='normal',
    help='HPC job queue to submit to.'
)
parser.add_argument(
    '--python',
    type=str,
    default=sys.executable,
    help='Python executable with which to run the task script.'
)

@functools.lru_cache()
def _args() -> argparse.Namespace:
    args = parser.parse_args()
    assert args.workers > 0
    assert args.ensemble_size > 0
    # assert os.path.exists(args.input)
    # assert os.path.exists(args.pairs)
    return args


def default_resources() -> dict:
    # Warning: Typo at
    # https://radicalpilot.readthedocs.io/en/stable/resources.html#frontera
    # says "xsede.frontera" when actually "tacc.frontera" is what is defined.
    resources = {
        'frontera': dict(
            default_db_url='mongodb://eirrgang:vBzHZ3qNryfOUh8X@95.217.193.116:27017/scalems',
            cpus_per_node=56,
            pilot_description={
                'resource': 'tacc.frontera',
                'access_schema': 'ssh',
            }
        ),
        'localhost': dict(
            default_db_url='mongodb://eirrgang:vBzHZ3qNryfOUh8X@95.217.193.116:27017/scalems',
            cpus_per_node=4,
            pilot_description={
                'resource': 'local.localhost',
                'access_schema': 'local',
            }
        )
    }
    return resources


class RunTime:
    """Configure and manage the runtime environment."""
    def __init__(self, config: argparse.Namespace):
        self.resource: dict = default_resources()[config.resource]
        self.cpus_per_node: int = self.resource['cpus_per_node']
        self.workers: int = config.workers
        self.db_url: str = os.getenv(
            'RADICAL_PILOT_DBURL',
            self.resource['default_db_url'])
        self.walltime_hours = config.walltime
        if self.resource['pilot_description']['resource'] == 'tacc.frontera':
            self.resource['pilot_description']['project'] = config.project
        self.queue = config.queue
        self._pilot_description = None

        if config.threads:
            self.cores: int = config.threads * self.workers
        else:
            self.cores: int = self.cpus_per_node * self.workers

    def pilot_description(self) -> rp.PilotDescription:
        if self._pilot_description is None:
            minutes = self.walltime_hours * 60
            pilot_description_dict = {
                'runtime': minutes,
                'cores': self.cores
            }
            pilot_description_dict.update(self.resource['pilot_description'])
            ncores: int = pilot_description_dict['cores']
            pilot_description_dict['queue'] = self.queue
            self._pilot_description = rp.PilotDescription(from_dict=pilot_description_dict)
        return self._pilot_description

    def make_session(self, **kwargs) -> rp.Session:
        session = rp.Session(dburl=self.db_url, **kwargs)

        if getattr(self.pilot_description(), 'resource', 'localhost') == 'tacc.frontera':
            context = rp.Context('ssh')
            context.user_id = 'rpilot'
            session.add_context(context)
        return session

    @contextlib.contextmanager
    def task_manager(self, session_args: dict = None):
        if session_args is None:
            session_args = {}
        with self.make_session(**session_args) as session:
            pilot: typing.Optional[rp.Pilot] = None
            pilot_manager = None
            task_manager = None
            try:
                pilot_manager = rp.PilotManager(session=session)
                task_manager = rp.TaskManager(session=session)
                pilot = pilot_manager.submit_pilots(self.pilot_description())
                pilot.wait(state=[rp.states.PMGR_ACTIVE] + rp.FINAL)
                assert pilot.state not in rp.FINAL

                task_manager.add_pilots(pilot)

                yield task_manager

            finally:
                if pilot is not None:
                    pilot.cancel()
                if task_manager is not None:
                    task_manager.close()
                if pilot_manager is not None:
                    pilot_manager.close()


class Work:
    """Configure and manage the BRER work."""
    def __init__(self, *, config: argparse.Namespace, runtime: RunTime):
        if config.threads:
            self.threads = config.threads
        else:
            self.threads = runtime.cpus_per_node

        self.script = pathlib.Path(config.task).absolute()

        self.pre_exec = ['unset OMP_NUM_THREADS']
        if config.pre is not None:
            self.pre_exec.extend(config.pre)

        self.input = os.path.abspath(config.input)
        self.pairs = os.path.abspath(config.pairs)
        self.workdir = os.path.abspath(config.workdir)
        self.ensemble_size = config.ensemble_size
        self.python = config.python

    def describe_tasks(self):
        for member in range(self.ensemble_size):
            # TaskDescription does not accept kwargs to initialize data members.
            # Ref https://radicalpilot.readthedocs.io/en/stable/apidoc.html#taskdescription
            task_description = rp.TaskDescription()
            # Make sure we execute with the expected venv.
            task_description.executable = self.python
            task_description.cpu_processes = 1
            task_description.cpu_threads = self.threads
            task_description.arguments = list([
                self.script,
                '--input',
                os.path.abspath(self.input),
                '--pairs',
                os.path.abspath(self.pairs),
                '--member',
                member,
                '--workdir',
                os.path.abspath(self.workdir),
                '--threads',
                self.threads
            ])
            task_description.pre_exec = self.pre_exec
            task_description.stage_on_error = True
            task_description.restartable = True
            task_description.stdout = f'brer{self.ensemble_size}_mem_{member}.out'
            task_description.stderr = f'brer{self.ensemble_size}_mem_{member}.err'
            task_description.output_staging = [
                {
                    'source': f'task:///{task_description.stdout}',
                    'target': 'client:///',
                    'action': rp.TRANSFER
                },
                {
                    'source': f'task:///{task_description.stderr}',
                    'target': 'client:///',
                    'action': rp.TRANSFER
                },
                {
                    'source': f'task:///brer{member}.log',
                    'target': f'client:///brer{self.ensemble_size}_mem_{member}.log',
                    'action': rp.TRANSFER
                },
            ]
            yield task_description


if __name__ == '__main__':
    os.umask(0o007)
    configuration = _args()
    runtime = RunTime(config=configuration)
    work = Work(config=configuration, runtime=runtime)

    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=DeprecationWarning,
                                module='radical.pilot.task_manager')
        warnings.filterwarnings('ignore', category=DeprecationWarning,
                                module='radical.pilot.db.database')
        warnings.filterwarnings('ignore', category=DeprecationWarning,
                                module='radical.pilot.session')
        with runtime.task_manager(session_args={'download': True}) as task_manager:
            tasks = task_manager.submit_tasks(
                descriptions=list(work.describe_tasks()))

            states = task_manager.wait_tasks()
