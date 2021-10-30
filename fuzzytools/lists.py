from __future__ import print_function
from __future__ import division
from __future__ import annotations
from . import _C

import numpy as np
import itertools
import random
from copy import copy, deepcopy

RANDOM_STATE = None
SHUFFLE = True

###################################################################################################################################################

def _check(l:list):
	assert isinstance(l, list)
	assert len(l)>0

def _check_not_empy(l:list):
	_check(l)
	assert len(l)>0

###################################################################################################################################################

def index_list(l, idxs):
	return list(np.array(l)[idxs])

def get_shuffled(l,
	shuffle=SHUFFLE,
	random_state=RANDOM_STATE,
	):
	new_l = deepcopy(l)
	if shuffle:
		random.seed(random_state)
		random.shuffle(new_l)
	return new_l

def get_shared_shuffled(*args,
	shuffle=SHUFFLE,
	random_state=RANDOM_STATE,
	):
	idxs = list(range(0, len(args[0])))
	new_idxs = get_shuffled(idxs,
		random_state=random_state,
		shuffle=shuffle,
		)
	new_args = []
	for l in args:
		new_args += [deepcopy(index_list(l, new_idxs))]
	return new_args

def check_same_class(elements):
	return all([type(e)==type(elements[0]) for e in elements])

def get_max_elements(elements):
	assert check_same_class(elements), 'all objects must be of the same class'
	max_elements = []
	max_e = max(elements)
	for e in elements:
		if e>=max_e:
			max_elements += [e]
	return [True if e in max_elements else False for e in elements]

def get_min_elements(elements):
	assert check_same_class(elements), 'all objects must be of the same class'
	min_elements = []
	min_e = min(elements)
	for e in elements:
		if e<=min_e:
			min_elements += [e]
	return [True if e in min_elements else False for e in elements]

def list_product(*args):
	return list(itertools.product(*args)) # just a wrap

def split_list_in_batches(l, batch_size):
	batches = []
	index = 0
	while index<len(l):
		batches.append(l[index:index+batch_size])
		index += batch_size
	return batches

def flat_list(list_of_lists):
	return sum(list_of_lists, [])

def get_random_item(l):
	_check_not_empy(l)
	idx = 0 if len(l)==1 else random.randint(0, len(l)-1)
	return l[idx]

def get_bootstrap(l:list, n,
	random_state=RANDOM_STATE,
	):
	'''
	with replacement
	faster than numpy.choice
	'''
	random.seed(random_state)
	return [get_random_item(l) for _ in range(0, n)]

def merge_lists(*args):
	merged = list(itertools.chain(*args))
	return merged

def delete_from_list(l:list, elements_to_remove:list):
	return [e for e in l if not e in elements_to_remove]

def all_elements_are_equal(l:list):
	return l.count(l[0])==len(l)

def check_unique_lists(l1, l2):
	uniques = True
	for x in l1:
		if x in l2:
			return False
	return uniques