from __future__ import print_function
from __future__ import division
from . import _C

import numpy as np
import random
from copy import copy, deepcopy

###################################################################################################################################################

def get_linspace_ranks(x, samples_per_range):
	i = 0
	sx = np.sort(x)
	ex_ranges = []
	while i<len(sx):
		sub_sx = sx[i:i+samples_per_range]
		ex_ranges.append(sub_sx)
		#print(sx[i:i+samples_per_range])
		i += samples_per_range

	if len(sub_sx)<samples_per_range:
		ex_ranges = ex_ranges[:-1]

	assert len(ex_ranges)>=2
	ranks = [ex_ranges[k][-1]+(ex_ranges[k+1][0]-ex_ranges[k][-1])/2 for k in range(len(ex_ranges)-1)]
	ranks = [sx[0]] + ranks + [sx[-1]]
	#print('ranks',ranks)
	rank_ranges = np.array([(ranks[k], ranks[k+1]) for k in range(len(ranks)-1)])
	#print('rank_ranges',rank_ranges)
	index_per_range = [np.where((x>ranks_i) & (x<=ranks_f)) for ranks_i,ranks_f in rank_ranges]
	return rank_ranges, index_per_range, ranks

def dropout_extreme_percentiles(x, p,
	mode:str='both',
	):
	assert p>=0
	if p==0:
		return x, np.arange(0, len(x))
	if mode=='both':
		valid_indexs = np.where((x>np.percentile(x, p)) & (x<np.percentile(x, 100-p)))
	elif mode=='lower': # dropout lower values
		valid_indexs = np.where(x>np.percentile(x, p))
	elif mode=='upper': # dropout upper values
		valid_indexs = np.where(x<np.percentile(x, 100-p))
	else:
		raise Exception(f'no mode {mode}')
	new_x = copy(x)[valid_indexs]
	return new_x, valid_indexs

def get_sigma_clipping_indexing(x, dist_mean, dist_sigma, sigma_m:float,
	apply_lower_bound:bool=True,
	):
	valid_indexs = np.ones(len(x)).astype(bool)
	valid_indexs &= x < dist_mean+dist_sigma*sigma_m # is valid if is in range
	if apply_lower_bound:
		valid_indexs &= x > dist_mean-dist_sigma*sigma_m # is valid if is in range
	return valid_indexs

def get_random_stratified_keys(keys, keys_classes, class_names, nc,
	random_seed=None,
	):
	d = {c:[] for c in class_names}
	indexs = list(range(0, len(keys)))
	if not random_seed is None:
		random.seed(random_seed)
	random.shuffle(indexs)
	i = 0
	while any([len(d[_c])<nc for _c in class_names]):
		index = indexs[i]
		key = keys[index]
		c = keys_classes[index]
		if len(d[c])<nc:
			d[c] += [key]
		i +=1
	return d

###################################################################################################################################################

def get_class_names(labels):
	uniques = np.unique(labels)
	return uniques

def get_nof_samples_cdict(labels,
	class_names=None,
	):
	uniques, counts = np.unique(labels, return_counts=True)
	class_names = uniques if class_names is None else class_names
	d = {}
	for c in class_names:
		v = counts[list(uniques).index(c)] if c in uniques else 0
		d[c] = v
	return d

def get_samples_cdict(objs, labels,
	class_names=None,
	):
	class_names = get_class_names(labels) if class_names is None else class_names
	d = {c:[] for c in class_names}
	for obj,label in zip(objs,labels):
		d[label] += [obj]
	return d