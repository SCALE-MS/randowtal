"""Demonstrate sample logic for an adaptive workflow.

This is a gmxapi 0.2 script to demonstrate sample logic for an adaptive workflow.
The script runs several ``run_brer`` tasks in a loop, deciding which pipelines to keep
running on successive iterations and (TBD) which configurations to add to the work load.

This script uses a fixed ensemble size, applying one MPI rank to each simulation.

Usage:
    python -m mpi4py workflow.py

"""

import logging

import gmxapi
from brer_task import run_brer

logger = logging.getLogger()

subgraph = gmxapi.subgraph(variables={'brer_phase': '', 'all_done': False})
with subgraph:
    brer = run_brer()
    subgraph.brer_phase = brer.phase
    subgraph.all_done

operation_instance = subgraph()
operation_instance.run()
assert operation_instance.values['float_with_default'] == 2.

loop = gmxapi.while_loop(operation=subgraph, condition=subgraph.bool_data)
handle = loop()
assert handle.output.float_with_default.result() == 6