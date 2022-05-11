from __future__ import print_function
from __future__ import division
from . import _C

import numpy as np
import math
from copy import copy, deepcopy
from ..strings import xstr
import math
import pandas as pd
from nested_dict import nested_dict
from .xerror import XError

NORMALIZE_MODE = 'true_label' # true_label predicted_label
K = 100

###################################################################################################################################################

def normalize_cm(cm, normalize_mode,
	k=K,
	):
	if normalize_mode=='true_label':
		new_cm = cm/np.sum(cm, axis=1)[:,None]*k
	elif normalize_mode=='predicted_label':
		new_cm = cm/np.sum(cm, axis=0)[None,:]*k
	elif normalize_mode is None:
		new_cm = copy(cm)
	else:
		raise Exception(f'normalize_mode={normalize_mode}')
	return new_cm

###################################################################################################################################################

class ConfusionMatrix():
	def __init__(self, cms, class_names,
		normalize_mode=NORMALIZE_MODE,
		cm_df=None,
		):
		if cm_df is None:
			self.generate_cm_df([normalize_cm(cm, normalize_mode) for cm in cms], class_names)
		else:
			self.cm_df = copy(cm_df)

	def size(self):
		return self.cm_df.values.shape

	def get_class_names(self):
		return list(self.cm_df.columns)

	def generate_cm_df(self, cms, class_names):
		cm_dict = nested_dict()
		size = cms[0].shape
		for i in range(0, size[0]):
			for j in range(0, size[1]):
				xe = XError([cm[i,j] for cm in cms])
				cm_dict[class_names[i]][class_names[j]] = xe
		self.cm_df = pd.DataFrame.from_dict(cm_dict, orient='index')

	def get_means(self):
		means = np.zeros(shape=self.size())
		for i in range(0, self.size()[0]):
			for j in range(0, self.size()[1]):
				means[i,j] = self.get_values()[i,j].get_mean()
		return means

	def get_stds(self):
		stds = np.zeros(shape=self.size())
		for i in range(0, self.size()[0]):
			for j in range(0, self.size()[1]):
				stds[i,j] = self.get_values()[i,j].get_std()
		return stds

	def get_diagonal_dict(self):
		d = {}
		for kc,c in enumerate(self.get_class_names()):
			d[c] = self.get_values()[kc,kc]
		return d

	def get_values(self):
		return self.cm_df.values

	def __repr__(self):
		return str(self.cm_df)

	def _ipython_display_(self):
		display(self.cm_df)

	def reorder_classes(self, new_classes):
		for c in new_classes:
			assert c in self.get_class_names()
		self.cm_df = self.cm_df.reindex(columns=new_classes)
		self.cm_df = self.cm_df.reindex(index=new_classes)
		self.class_names = deepcopy(new_classes)

	def __add__(self, other):
		if self is None or self==0:
			return other

		elif other is None or other==0:
			return self
			
		elif type(self)==ConfusionMatrix and type(other)==ConfusionMatrix:
			assert self.size()==other.size()
			assert self.get_class_names()==other.get_class_names()
			new_cm_df = self.cm_df.add(other.cm_df)
			new_cm = ConfusionMatrix(None, None, cm_df=new_cm_df)
			return new_cm

		else:
			raise Exception(f'{type(self)}; {type(other)}')

	def __radd__(self, other):
		return self+other

	def __truediv__(self, other):
		new_cm_df = self.cm_df/other
		new_cm = ConfusionMatrix(None, None, cm_df=new_cm_df)
		return new_cm

	def __rmul__(self, other):
		return self*other