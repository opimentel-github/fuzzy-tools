from __future__ import print_function
from __future__ import division
from . import _C

from sklearn import metrics as skmetrics
import numpy as np
import math
from nested_dict import nested_dict
from . import labels as ds_labels
from copy import copy, deepcopy

EPS = 1e-10
CHECK_DISTRIBUTION = False

# https://stackoverflow.com/questions/53977031/precision-score-does-not-match-with-metrics-formula
# https://machinelearningmastery.com/roc-curves-and-precision-recall-curves-for-classification-in-python/#:~:text=ROC%20Curves%20and%20AUC%20in%20Python,-We%20can%20plot&text=The%20function%20takes%20both%20the,for%20each%20threshold%20and%20thresholds.
# https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_curve.html#sklearn.metrics.roc_curve

###################################################################################################################################################

def get_cm(_y_pred, _y_true, class_names,
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

	y_true = _y_true.copy()
	if target_is_onehot:
		assert len(y_true.shape)==2
		assert y_true.shape[-1]==len(class_names)
		y_true = y_true.argmax(axis=-1)

	assert y_pred.shape==y_true.shape
	cm = skmetrics.confusion_matrix(y_true, y_pred)
	return cm

###################################################################################################################################################

class BinBatchCM():
	def __init__(self, y_pred, y_true, class_names,
		pos_probability=[],
		pos_label=1,
		):
		assert len(class_names)==2
		assert pos_label in [0, 1]

		self.y_pred = copy(y_pred)
		self.y_true = copy(y_true)
		self.class_names = class_names
		self.pos_probability = copy(pos_probability)
		self.pos_label = pos_label
		self.reset()

	def reset(self):
		self.bin_cm = get_cm(self.y_pred, self.y_true, self.class_names)
		#print('y_pred',self.y_pred)
		#print('y_true',self.y_true)
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
		return tp/(tp+fp+EPS)

	def get_recall(self):
		tp, fn, fp, tn = self.get_cm_elements()
		return tp/(tp+fn+EPS)

	def get_specifity(self):
		tp, fn, fp, tn = self.get_cm_elements()
		return tn/(tn+fp+EPS)

	def get_accuracy(self):
		tp, fn, fp, tn = self.get_cm_elements()
		return (tp+tn)/(tp+fn+fp+tn+EPS)

	def get_gmean(self):
		recall = self.get_recall()
		specifity = self.get_specifity()
		return math.sqrt(recall*specifity)

	def get_dpower(self):
		recall = self.get_recall()
		specifity = self.get_specifity()
		x = recall/(1-recall+EPS)
		y = specifity/(1-specifity+EPS)
		return math.sqrt(3.)/math.pi*(math.log(x+EPS)+math.log(y+EPS))

	def get_fscore(self, beta):
		precision = self.get_precision()
		recall = self.get_recall()
		return (1+beta**2)*(precision*recall)/((beta**2*precision)+recall+EPS)

	def get_f1score(self):
		return self.get_fscore(1)

	def _get_pos_p(self):
		pos_p = self.pos_probability
		pos_y_true = self.y_true==self.pos_label
		assert np.sum(pos_y_true)<len(pos_y_true), 'needs samples from both classes'
		return pos_y_true, pos_p

	def get_xentropy(self):
		pos_y_true, pos_p = self._get_pos_p()
		return np.mean(-1*np.log(pos_p+EPS))

	def get_prc(self):
		pos_y_true, pos_p = self._get_pos_p()
		precision, recall, thresholds = skmetrics.precision_recall_curve(pos_y_true, pos_p)
		d = {
			'recall':recall,
			'precision':precision,
			'thresholds':thresholds,
			'_len':len(recall),
			}
		return d

	def get_aucpr(self):
		pos_y_true, pos_p = self._get_pos_p()
		aucpr = skmetrics.average_precision_score(pos_y_true, pos_p, pos_label=1)
		return aucpr

	def get_rocc(self):
		pos_y_true, pos_p = self._get_pos_p()
		fpr, tpr, thresholds = skmetrics.roc_curve(pos_y_true, pos_p)
		d = {
			'fpr':fpr,
			'tpr':tpr,
			'thresholds':thresholds,
			'_len':len(fpr),
			}
		return d

	def get_aucroc(self):
		pos_y_true, pos_p = self._get_pos_p()
		aucroc = skmetrics.roc_auc_score(pos_y_true, pos_p)
		return aucroc

###################################################################################################################################################

def get_multiclass_metrics(_y_pred_p, _y_true, class_names,
	metrics=[
		'precision',
		'recall',
		'f1score',
		'accuracy',
		'gmean',
		'dpower',
		'prc',
		'aucpr',
		'rocc',
		'aucroc',
		'xentropy',
		],
	check_distribution=CHECK_DISTRIBUTION,
	):
	### checks
	assert len(class_names)>2
	y_pred_p, y_pred, y_true = ds_labels.format_labels(_y_pred_p, _y_true, class_names,
		check_distribution=check_distribution,
		)

	### compute for each binary cm case
	metrics_cdict = nested_dict()
	for kc,c in enumerate(class_names):
		y_true_c = ((y_true==kc)).astype(int)
		y_pred_c = ((y_pred==kc)).astype(int)
		pos_probability_c = y_pred_p[:,kc]
		bin_bach_cm = BinBatchCM(y_pred_c, y_true_c, [f'non-{c}', f'c'], pos_probability=pos_probability_c, pos_label=1)
		for m in metrics:
			metrics_cdict[c][m] = getattr(bin_bach_cm, f'get_{m}')()
	metrics_cdict = metrics_cdict.to_dict()

	### get cm
	y_pred = y_pred_p.argmax(axis=-1)
	cm = get_cm(y_pred, y_true, class_names)

	### compute averages results
	support = {c:cm[kc].sum() for kc,c in enumerate(class_names)}
	total_samples = sum(support[c] for c in class_names)
	metrics_dict = {}
	for m in metrics:
		if isinstance(metrics_cdict[class_names[0]][m], dict):
			continue
		metrics_dict[f'b-{m}'] = sum([1*metrics_cdict[c][m] for c in class_names])/len(class_names)
		metrics_dict[f'w-{m}'] = sum([support[c]*metrics_cdict[c][m] for c in class_names])/total_samples
		
	return metrics_cdict, metrics_dict, cm