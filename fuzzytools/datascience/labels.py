from __future__ import print_function
from __future__ import division
from . import _C

from sklearn import metrics as skmetrics
import numpy as np
import math
from nested_dict import nested_dict
from copy import copy, deepcopy

EPS = _C.EPS
CHECK_DISTRIBUTION = False

###################################################################################################################################################

def _check_int(y_true):
	assert 'int' in str(y_true.dtype)

def _check_bool(y_true):
	assert 'bool' in str(y_true.dtype)

def _check_labels(y_pred_p, y_true, class_names,
	check_distribution=CHECK_DISTRIBUTION,
	):
	'''
	y_pred_p: (b,c)
	y_true: (b)/(b,c)
	class_names: [c]
	'''
	### y_pred_p
	if not y_pred_p is None:
		assert len(y_true)==len(y_pred_p)
		assert len(y_pred_p.shape)==2
		assert y_pred_p.shape[-1]==len(class_names)
		assert np.all(y_pred_p>=0) and np.all(y_pred_p<=1)
		if check_distribution:
			assert np.all((1-np.sum(y_pred_p, axis=-1))**2<=EPS)

	### y_true
	assert len(y_true.shape)==1 or len(y_true.shape)==2
	y_true_is_onehot = len(y_true.shape)==2
	if y_true_is_onehot:
		_check_bool(y_true)
	else:
		_check_int(y_true)

	return y_true_is_onehot

###################################################################################################################################################

def get_onehot(y_true,
	class_names=None,
	):
	assert len(y_true.shape)==1
	_check_int(y_true)

	class_count = np.max(y_true)+1 if class_names is None else len(class_names)
	return np.eye(class_count)[y_true].astype(np.bool)

def format_labels(y_pred_p, y_true, class_names,
	check_distribution=CHECK_DISTRIBUTION,
	):
	y_true_is_onehot = _check_labels(y_pred_p, y_true, class_names,
		check_distribution,
		)

	### y_true
	if y_true_is_onehot:
		new_y_true = np.argmax(y_true, axis=-1) # (b,c)>(b)
	else:
		new_y_true = copy(y_true)

	### pred
	if y_pred_p is None:
		new_y_pred_p = None
		y_pred = None
	else:
		new_y_pred_p = copy(y_pred_p)
		y_pred = np.argmax(y_pred_p, axis=-1)
	return new_y_pred_p, y_pred, new_y_true
