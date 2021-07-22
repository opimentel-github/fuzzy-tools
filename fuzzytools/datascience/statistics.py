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

def get_populations_cdict(labels, class_names):
	uniques, counts = np.unique(labels, return_counts=True)
	d = {}
	for c in class_names:
		v = counts[list(uniques).index(c)] if c in uniques else 0
		d[c] = v
	return d

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

def stratified_kfold_split(obj_names, obj_classes_, class_names, new_sets_props, kfolds,
	random_state=0,
	permute=False,
	eps=_C.EPS,
	):
	sum_ = sum([new_sets_props[k] for k in new_sets_props.keys()])
	assert abs(1-sum_)<=eps
	assert len(new_sets_props.keys())>=2
	
	new_sets_props_len = len(new_sets_props.keys())
	obj_names_len = len(obj_names)
	obj_classes_d = {obj_name:obj_classes_[k] for k,obj_name in enumerate(obj_names)}
	populations_cdict = get_populations_cdict(obj_classes_, class_names)
	
	_obj_names = obj_names.copy()
	if permute:
		random.seed(random_state)
		random.shuffle(_obj_names) # permute
	
	obj_names_kdict = {}
	for kf in range(kfolds):
		obj_names_kf = [obj_name for obj_name in _obj_names]
		shift_n = (obj_names_len//kfolds)*kf
		obj_names_kf = obj_names_kf[shift_n:]+obj_names_kf[:shift_n] # shift list!!
		#print(obj_names_kf)
		
		for ks,new_sets_prop_k in enumerate(new_sets_props.keys()):
			obj_names_kdict[f'{kf}{_C.KFOLF_CHAR}{new_sets_prop_k}'] = []
			
			for kc,c in enumerate(class_names):
				to_fill_pop = round(populations_cdict[c]*new_sets_props[new_sets_prop_k])
				#print(kf, new_sets_prop_k, c, to_fill_pop)
				obj_classes = np.array([obj_classes_d[obj_name] for obj_name in obj_names_kf])
				valid_indexs = np.where(obj_classes==c)[0][:to_fill_pop] if ks<=new_sets_props_len-2 else np.where(obj_classes==c)[0]
				#print(kf, new_sets_prop_k, c, valid_indexs, len(obj_names_kf))
				obj_names_to_add = [obj_names_kf[valid_index] for valid_index in valid_indexs]
				for obj_name_to_add in obj_names_to_add:
					obj_names_kdict[f'{kf}{_C.KFOLF_CHAR}{new_sets_prop_k}'].append(obj_name_to_add)
					obj_names_kf.pop(obj_names_kf.index(obj_name_to_add)) # remove from list

	return obj_names_kdict