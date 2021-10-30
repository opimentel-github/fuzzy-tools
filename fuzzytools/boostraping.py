from __future__ import print_function
from __future__ import division
from . import _C

from . import strings
from itertools import cycle
from copy import copy, deepcopy
import random
import numpy as np

###################################################################################################################################################

class BalancedCyclicBoostraping():
	def __init__(self, l_objs, l_classes,
		batch_prop=1,
		uses_shuffle=True,
		uses_counter=False,
		samples_per_class=None,
		):
		assert len(l_objs)==len(l_classes)
		assert batch_prop>=0 and batch_prop<=1
		self.l_objs = l_objs
		self.l_classes = l_classes
		self.batch_prop = batch_prop
		self.uses_shuffle = uses_shuffle
		self.uses_counter = uses_counter
		self.samples_per_class = samples_per_class
		self.reset()

	def reset(self):
		if len(self)==0:
			return
		self.class_names, counts = np.unique(self.l_classes, return_counts=True)
		self.samples_per_class = int(max(counts)*self.batch_prop) if self.samples_per_class is None else self.samples_per_class
		self.reset_counter()
		self.l_objs_dict = {}
		for c in self.class_names:
			self.l_objs_dict[c] = [obj for obj,_c in zip(self.l_objs, self.l_classes) if _c==c]
		self.reset_cycles()

	def get_class_names(self):
		return self.class_names

	def get_nof_samples(self):
		return len(self.l_objs)

	def __len__(self):
		return len(self.get_class_names())*self.samples_per_class

	def get_n(self):
		return self.samples_per_class

	def __repr__(self):
		txt = f'BalancedCyclicBoostraping('
		txt += strings.get_string_from_dict({
			'batch_prop':self.batch_prop,
			'samples_per_class':self.samples_per_class,
			'nof_samples':self.get_nof_samples(),
			'__len__':len(self),
			}, '; ', '=')
		txt += ')'
		return txt

	def reset_counter(self):
		self.counter = {obj:0 for obj in self.l_objs}

	def reset_cycles(self):
		if self.uses_shuffle:
			self.shuffle()
		self.cycles_dict = {c:cycle(self.l_objs_dict[c]) for c in self.class_names}
	
	def shuffle(self):
		for c in self.class_names:
			random.shuffle(self.l_objs_dict[c])
			
	def get_size(self):
		return self.n*len(self.class_names)
	
	def get_samples(self):
		samples = []
		for c in self.class_names:
			samples += [next(self.cycles_dict[c]) for _ in range(0, self.samples_per_class)]
		if self.uses_counter:
			for s in samples:
				self.counter[s] += 1
		return samples
	
	def __call__(self):
		return self.get_samples()