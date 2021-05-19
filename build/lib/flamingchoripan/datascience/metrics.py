from __future__ import print_function
from __future__ import division
from . import C_

from sklearn import metrics as skmetrics
from sklearn.metrics import precision_recall_fscore_support as skmetrics_full
import numpy as np

def get_cm_accuracy(y_pred, y_target,
	pred_is_onehot:bool=True,
	target_is_onehot:bool=False,
	):
	'''
	axis=-1 is true labels
	'''
	y_pred = y_pred.argmax(axis=-1) if pred_is_onehot else np.copy(y_pred)
	y_target = y_target.argmax(axis=-1) if target_is_onehot else np.copy(y_target)
	assert y_pred.shape==y_target.shape

	cm = skmetrics.confusion_matrix(y_target, y_pred)
	accuracy = np.sum(np.diagonal(cm))/np.sum(cm)
	return cm, accuracy*100

def get_baccuracy_c(y_pred, y_target, class_names,
	pred_is_onehot:bool=True,
	target_is_onehot:bool=False,
	return_cm:bool=False,
	**kwargs):
	cm,_ = get_cm_accuracy(y_pred, y_target,
	pred_is_onehot,
	target_is_onehot,
	)
	accu_per_class = np.diagonal(cm)/np.sum(cm, axis=-1)*100
	accu_cdict = {c:accu_per_class[kc] for kc,c in enumerate(class_names)}
	if return_cm:
		return accu_cdict, accu_per_class.mean(), cm
	return accu_cdict, accu_per_class.mean()

def get_precision_recall_f1score_c(y_pred, y_target, class_names,
	pred_is_onehot:bool=True,
	target_is_onehot:bool=False,
	**kwargs):
	y_pred = y_pred.argmax(axis=-1) if pred_is_onehot else np.copy(y_pred)
	y_target = y_target.argmax(axis=-1) if target_is_onehot else np.copy(y_target)
	assert y_pred.shape==y_target.shape

	precision, recall, f1score, y_target_support = skmetrics_full(y_target, y_pred, beta=1)
	total_samples = sum(y_target_support)
	scores_cdict = {
		'precision':{c:precision[kc] for kc,c in enumerate(class_names)},
		'recall':{c:recall[kc] for kc,c in enumerate(class_names)},
		'f1score':{c:f1score[kc] for kc,c in enumerate(class_names)},
		'true_samples':{c:y_target_support[kc] for kc,c in enumerate(class_names)},
	}
	scores_dict = {
		'b-precision':precision.mean(),
		'b-recall':recall.mean(),
		'b-f1score':f1score.mean(),
	}
	return scores_cdict, scores_dict

def get_all_metrics_c(y_pred, y_target, class_names,
	pred_is_onehot:bool=True,
	target_is_onehot:bool=False,
	**kwargs):
	baccu_cdict, baccu, cm = get_baccuracy_c(y_pred, y_target, class_names,
		pred_is_onehot,
		target_is_onehot,
		return_cm=True,
		**kwargs)
	scores_cdict, scores_dict = get_precision_recall_f1score_c(y_pred, y_target, class_names,
		pred_is_onehot,
		target_is_onehot,
		**kwargs)

	for key in scores_cdict.keys():
		scores_cdict[key]['accuracy'] = {c:baccu_cdict[c] for kc,c in enumerate(class_names)}
	scores_dict.update({'b-accuracy':baccu})
	return scores_cdict, scores_dict, cm