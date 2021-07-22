from __future__ import print_function
from __future__ import division
from __future__ import annotations
from . import _C

import itertools
import random

###################################################################################################################################################

def _check(l:list):
	assert isinstance(l, list)
	assert len(l)>0

def _check_not_empy(l:list):
	_check(l)
	assert len(l)>0

###################################################################################################################################################

def check_same_class(elements):
	return all([type(e)==type(elements[0]) for e in elements])

def get_max_elements(elements):
	assert check_same_class(elements), 'all objects must be of the same class'
	max_elements = []
	max_e = max(elements)
	#print(max_e, elements)
	for e in elements:
		if e>=max_e:
			max_elements += [e]
	return [True if e in max_elements else False for e in elements]

def get_min_elements(elements):
	assert check_same_class(elements), 'all objects must be of the same class'
	min_elements = []
	min_e = min(elements)
	#print(min_e, elements)
	for e in elements:
		if e<=min_e:
			min_elements += [e]
	return [True if e in min_elements else False for e in elements]

def split_list_in_batches(l, batch_size):
	batches = []
	index = 0
	while index<len(l):
		batches.append(l[index:index+batch_size])
		index += batch_size
	return batches
	
def list_product(*args):
	return list(itertools.product(*args)) # just a wrap

def flat_list(list_of_lists:List[list]):
	return sum(list_of_lists, [])

def get_random_item(l):
	_check_not_empy(l)
	idx = 0 if len(l)==1 else random.randint(0, len(l)-1)
	return l[idx]

def get_random_key(d:dict):
	keys = list(d.keys())
	key = get_random_item(keys)
	return key

def get_bootstrap(l:list, n,
	random_state=None,
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

def all_elements_equals(l:list):
	return l.count(l[0])==len(l)