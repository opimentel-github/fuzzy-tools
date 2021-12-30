from __future__ import print_function
from __future__ import division
from . import _C

from . import strings
from itertools import cycle
from copy import copy, deepcopy
import random
import numpy as np

BATCH_PROP = 1

###################################################################################################################################################

class BalancedCyclicBoostraping():
	def __init__(self, l_objs, l_classes,
		batch_prop=BATCH_PROP,
		uses_shuffle=True,
		samples_per_class=None,
		class_names=None,
		):
		assert len(l_objs)==len(l_classes)
		assert batch_prop>=0 and batch_prop<=1
		self.l_objs = l_objs
		self.l_classes = l_classes
		self.batch_prop = batch_prop
		self.uses_shuffle = uses_shuffle
		self.samples_per_class = samples_per_class
		self.class_names = class_names
		self.reset()

	def reset(self):
		self.class_names = np.unique(self.l_classes) if self.class_names is None else self.class_names
		self.samples_per_class = int(self.get_majority_class_nof_samples()*self.batch_prop) if self.samples_per_class is None else self.samples_per_class
		self.l_objs_dict = {}
		for c in self.class_names:
			self.l_objs_dict[c] = [obj for obj,_c in zip(self.l_objs, self.l_classes) if _c==c]
		self.reset_cycles()

	def reset_cycles(self):
		if self.uses_shuffle:
			self.shuffle()
		self.cycles_dict = {c:cycle(self.l_objs_dict[c]) for c in self.class_names}

	def get_majority_class_nof_samples(self):
		class_names, counts = np.unique(self.l_classes, return_counts=True)
		return max(counts)

	def get_class_names(self):
		return self.class_names

	def get_nof_classes(self):
		return len(self.get_class_names())

	def get_nof_samples(self):
		return len(self.l_objs)

	def __len__(self):
		return self.get_nof_classes()*self.samples_per_class

	def get_samples_per_class(self):
		return self.samples_per_class

	def __repr__(self):
		txt = f'BalancedCyclicBoostraping('
		txt += strings.get_string_from_dict({
			'batch_prop':self.batch_prop,
			'samples_per_class':self.samples_per_class,
			'nof_samples':self.get_nof_samples(),
			'nof_classes':self.get_nof_classes(),
			'_len':len(self),
			}, '; ', '=')
		txt += ')'
		return txt
	
	def shuffle(self):
		for c in self.class_names:
			random.shuffle(self.l_objs_dict[c])
			
	def get_size(self):
		return self.n*len(self.class_names)
	
	def get_samples(self):
		samples = []
		for c in self.class_names:
			for _ in range(0, self.samples_per_class):
				samples_c = next(self.cycles_dict[c])
				samples += [samples_c]
		return samples
	
	def __call__(self):
		return self.get_samples()