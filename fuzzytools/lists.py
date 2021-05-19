from __future__ import print_function
from __future__ import division
from __future__ import annotations
from . import C_

import itertools
import random

###################################################################################################################################################

def get_list_chunks(l, chuncks_size):
	chuncks = []
	index = 0
	while index<len(l):
		chuncks.append(l[index:index+chuncks_size])
		index += chuncks_size
	return chuncks
	
def list_product(*args):
	return list(itertools.product(*args)) # just a wrap

def flat_list(list_of_lists:List[list]):
	return sum(list_of_lists, [])

def get_random_item(l:list):
	return l[random.randint(0, len(l)-1)]

def get_random_key(d:dict):
	return get_random_item(list(d.keys()))

def get_random_subsampled_list(l:list, n):
	return [get_random_item(l) for _ in range(n)]

def merge_lists(*args):
	merged = list(itertools.chain(*args))
	return merged

def delete_from_list(l:list, elements_to_remove:list):
	return [e for e in l if not e in elements_to_remove]

def all_elements_equals(l:list):
	return l.count(l[0])==len(l)