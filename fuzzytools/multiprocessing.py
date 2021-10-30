from __future__ import print_function
from __future__ import division
from . import _C

import os
from .lists import split_list_in_batches

BACKEND = 'multiprocessing' # loky multiprocessing threading
N_PROCESS = None
M = 5

# https://medium.com/contentsquare-engineering-blog/multithreading-vs-multiprocessing-in-python-ece023ad55a
###################################################################################################################################################

def get_joblib_config(
	backend=BACKEND,
	n_process=N_PROCESS,
	m=M,
	):
	if backend is None:
		return 1
	cpus = os.cpu_count()
	if backend in ['loky', 'multiprocessing']:
		n_jobs = cpus if n_process is None else n_process
		assert n_jobs<=cpus
		return n_jobs

	elif backend=='threading':
		n_jobs = m*cpus
		return n_jobs

	else:
		raise Exception(f'invalid backend={backend}')

def get_joblib_config_batches(l,
	backend=BACKEND,
	n_process=N_PROCESS,
	m=M,
	):
	n_jobs = get_joblib_config(
		backend,
		n_process,
		m,
		)
	batch_size = n_jobs
	batches = split_list_in_batches(l, batch_size)
	return batches, n_jobs