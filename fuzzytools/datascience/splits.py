from __future__ import print_function
from __future__ import division
from . import _C

import numpy as np
import random
from .statistics import get_samples_cdict
from sklearn.model_selection import StratifiedKFold
from nested_dict import nested_dict
from .. import lists
from copy import copy, deepcopy

RANDOM_STATE = None
KFOLF_CHAR = _C.KFOLF_CHAR
ALL_CHAR = '.'

###################################################################################################################################################

def shift_dict(d, k, prop):
	new_d = deepcopy(d)
	for key in new_d.keys():
		shift_n = int(len(new_d[key])*prop*k)
		new_d[key] = new_d[key][shift_n:]+new_d[key][:shift_n] # shift list!
	return new_d

def split_list(l, prop):
	last_index = int(len(l)*prop)
	first_half, last_half = l[:last_index], l[last_index:]
	return first_half, last_half

def stratifiedf_kfold_cyclic_311(_obj_names, _obj_classes,
	shuffle=False,
	random_state=RANDOM_STATE,
	outlier_obj_names=[],
	prefix_str='',
	returns_populations_cdict=False,
	):
	obj_names, obj_classes = lists.get_shared_shuffled(_obj_names, _obj_classes,
		shuffle=shuffle,
		random_state=random_state,
		)
	populations_cdict = get_samples_cdict(obj_names, obj_classes)
	class_names = list(populations_cdict.keys())

	# detele outliers
	for c in class_names:
		populations_cdict[c], _ = lists.delete_from_list(populations_cdict[c], outlier_obj_names)

	# create folds
	kfolds = list(f'{k}' for k in range(0, 5))
	obj_names_kdict = {}
	for k,kf in enumerate(kfolds):
		kf_populations_cdict = shift_dict(populations_cdict, k, 1/5)
		obj_names_kdict[f'{kf}{KFOLF_CHAR}{prefix_str}train'] = []
		obj_names_kdict[f'{kf}{KFOLF_CHAR}{prefix_str}val'] = []
		obj_names_kdict[f'{kf}{KFOLF_CHAR}{prefix_str}test'] = []
		for c in class_names:
			last_half = kf_populations_cdict[c]
			first_half, last_half = split_list(last_half, 3/5)
			obj_names_kdict[f'{kf}{KFOLF_CHAR}{prefix_str}train'] += first_half
			first_half, last_half = split_list(last_half, 1/2)
			obj_names_kdict[f'{kf}{KFOLF_CHAR}{prefix_str}val'] += first_half
			obj_names_kdict[f'{kf}{KFOLF_CHAR}{prefix_str}test'] += last_half

	if returns_populations_cdict:
		return obj_names_kdict, class_names, kfolds, populations_cdict
	else:
		return obj_names_kdict, class_names, kfolds