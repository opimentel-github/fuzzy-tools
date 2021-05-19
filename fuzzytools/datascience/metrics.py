from __future__ import print_function
from __future__ import division
from . import C_

from sklearn import metrics as skmetrics
import numpy as np
import math
from nested_dict import nested_dict

###################################################################################################################################################

def _check_prob(y_pred_p, class_names):
	assert len(y_pred_p.shape)==2
	assert y_pred_p.shape[-1]==len(class_names)
	assert np.all(y_pred_p>=0)
	assert np.all(y_pred_p<=1)
	#assert np.all((1-np.sum(y_pred_p, axis=-1))**2<=C_.EPS)

def get_cm(_y_pred, _y_target, class_names,
	pred_is_onehot:bool=False,
	target_is_onehot:bool=False,
	):
	'''
	axis=-1 is true labels
	'''
	y_pred = _y_pred.copy()
	if pred_is_onehot:
		assert len(y_pred.shape)==2
		assert y_pred.shape[-1]==len(class_names)
		y_pred = y_pred.argmax(axis=-1)

	y_target = _y_target.copy()
	if target_is_onehot:
		assert len(y_target.shape)==2
		assert y_target.shape[-1]==len(class_names)
		y_target = y_target.argmax(axis=-1)

	assert y_pred.shape==y_target.shape
	cm = skmetrics.confusion_matrix(y_target, y_pred)
	return cm

###################################################################################################################################################

class BinBatchCM():
	def __init__(self, y_pred, y_target, class_names,
		pos_probability=[],
		pos_label=1,
		):
		assert len(class_names)==2
		assert pos_label in [0, 1]

		self.y_pred = y_pred.copy()
		self.y_target = y_target.copy()
		self.class_names = class_names
		self.pos_probability = pos_probability.copy()
		self.pos_label = pos_label
		self.reset()

	def reset(self):
		self.bin_cm = get_cm(self.y_pred, self.y_target, self.class_names)
		#print('y_pred',self.y_pred)
		#print('y_target',self.y_target)
		#print('bin_cm',self.bin_cm)
		assert len(self.bin_cm.shape)==2
		assert self.bin_cm.shape[0]==2
		assert self.bin_cm.shape[0]==2
		#i = 0
		#(self.bin_cm[0][0],self.bin_cm[1][1]) = (self.bin_cm[1][1],self.bin_cm[0][0])
		self.tn = self.bin_cm[0,0]
		self.tp = self.bin_cm[1,1]
		self.fn = self.bin_cm[1,0]
		self.fp = self.bin_cm[0,1]
		#self.tn, self.fp, self.fn, self.tp = self.bin_cm.ravel()
		#self.tp, self.fn, self.fp, self.tn = self.bin_cm.ravel()
		#print(self.tn, self.fp, self.fn, self.tp)

	def get_cm_elements(self):
		return self.tp, self.fn, self.fp, self.tn

	def get_precision(self):
		tp, fn, fp, tn = self.get_cm_elements()
		return tp/(tp+fp+C_.EPS)

	def get_recall(self):
		tp, fn, fp, tn = self.get_cm_elements()
		return tp/(tp+fn+C_.EPS)

	def get_specifity(self):
		tp, fn, fp, tn = self.get_cm_elements()
		return tn/(tn+fp+C_.EPS)

	def get_accuracy(self):
		tp, fn, fp, tn = self.get_cm_elements()
		return (tp+tn)/(tp+fn+fp+tn+C_.EPS)

	def get_gmean(self):
		recall = self.get_recall()
		specifity = self.get_specifity()
		return math.sqrt(recall*specifity)

	def get_dpower(self):
		recall = self.get_recall()
		specifity = self.get_specifity()
		x = recall/(1-recall+C_.EPS)
		y = specifity/(1-specifity+C_.EPS)
		return math.sqrt(3.)/math.pi*(math.log(x+C_.EPS)+math.log(y+C_.EPS))

	def get_fscore(self, beta):
		precision = self.get_precision()
		recall = self.get_recall()
		return (1+beta**2)*(precision*recall)/((beta**2*precision)+recall+C_.EPS)

	def get_f1score(self):
		return self.get_fscore(1)

	def get_xentropy(self):
		p = self.pos_probability
		return np.mean(-1*np.log(p+C_.EPS))

	def get_prauc(self):
		p = self.pos_probability
		y_target = self.y_target==self.pos_label
		return skmetrics.average_precision_score(y_target, p, pos_label=1)

	def get_rocauc(self):
		p = self.pos_probability
		y_target = self.y_target==self.pos_label
		return skmetrics.roc_auc_score(self.y_target, p)

###################################################################################################################################################
#https://stackoverflow.com/questions/53977031/precision-score-does-not-match-with-metrics-formula
def get_multiclass_metrics(_y_pred_p, _y_target, class_names,
	metrics=['accuracy', 'precision', 'recall', 'f1score', 'prauc', 'rocauc'],#, 'xentropy'],
	target_is_onehot:bool=False,
	):
	### checks
	y_target = _y_target.copy()
	y_pred_p = _y_pred_p.copy()
	_check_prob(y_pred_p, class_names)
	assert len(class_names)>2
	assert len(y_pred_p)==len(y_target)

	### compute for each binary cm case
	y_target = y_target.argmax(axis=-1) if target_is_onehot else np.copy(y_target)
	y_pred = y_pred_p.argmax(axis=-1)
	metrics_cdict = nested_dict()
	for kc,c in enumerate(class_names):
		y_target_c = ((y_target==kc)).astype(int)
		y_pred_c = ((y_pred==kc)).astype(int)
		pos_probability_c = y_pred_p[:,kc]
		bin_bach_cm = BinBatchCM(y_pred_c, y_target_c, [f'non-{c}', f'c'], pos_probability=pos_probability_c, pos_label=1)
		for m in metrics:
			metrics_cdict[c][m] = getattr(bin_bach_cm, f'get_{m}')()

		#print(metrics_cdict)
		#assert 0
	metrics_cdict = metrics_cdict.to_dict()

	### get cm
	y_pred = y_pred_p.argmax(axis=-1)
	cm = get_cm(y_pred, y_target, class_names)

	### compute averages results
	support = {c:cm[kc].sum() for kc,c in enumerate(class_names)}
	total_samples = sum(support[c] for c in class_names)
	metrics_dict = {}
	for m in metrics:
		metrics_dict[f'b-{m}'] = sum([1*metrics_cdict[c][m] for c in class_names])/len(class_names)
		metrics_dict[f'w-{m}'] = sum([support[c]*metrics_cdict[c][m] for c in class_names])/total_samples
		
	return metrics_cdict, metrics_dict, cm