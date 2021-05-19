from __future__ import print_function
from __future__ import division
from . import C_

import numpy as np
import math
from ..strings import xstr
import random
import pandas as pd

###################################################################################################################################################

class XError():
	def __init__(self, x,
		dim:int=0,
		error_scale=1,
		n_decimals=C_.N_DECIMALS,
		mode='mean/std',
		):
		self.is_dummy = x is None or len(x)==0
		if self.is_dummy:
			self.x = []
		else:
			assert len(x)>0
			self.x = np.array(x).copy()
		self.dim = dim
		self.error_scale = error_scale
		self.n_decimals = n_decimals
		self.mode = mode
		
		### calculate statistics
		if not self.is_dummy:
			self.mean = self.get_mean()
			self.median = self.set_percentile(50)
			self.std = self.get_std()
			self.serror = self.get_serror()
			
			for p in [1, 5, 10, 15]:
				self.set_percentile(p)
				self.set_percentile(100-p)

			self.dsymbols = {
				'std':C_.STD_LATEXCHAR,
				'serror':C_.SERROR_LATEXCHAR,
			}

	def set_percentile(self, p:int):
		percentile = np.percentile(self.x, p, axis=self.dim)
		setattr(self, f'p{p}', percentile)
		return percentile

	def get_mean(self):
		return np.mean(self.x, axis=self.dim)

	def get_std(self):
		std = np.std(self.x, axis=self.dim)*self.error_scale
		return std

	def get_serror(self):
		'''
		Standar Error = sqrt(sum((x-x_mean)**2)/(N-1)) / sqrt(N)
		'''
		if len(self)>1:
			return np.std(self.x, axis=self.dim, ddof=1)/math.sqrt(self.x.shape[self.dim])*self.error_scale
		else:
			return self.get_std()

	def get_symbol(self, attr):
		return f'{self.error_scale}{self.dsymbols[attr]}'

	def __len__(self):
		return 0 if self.is_dummy else self.x.shape[self.dim]

	def __repr__(self):
		if self.is_dummy:
			return f'{xstr(None)}'
		else:
			return f'{xstr(self.mean, self.n_decimals)}{C_.PM_CHAR}{xstr(self.std, self.n_decimals)}'

	def __gt__(self, other):
		if other==0 or other is None:
			return self.mean-self.std > 0
		elif other.is_dummy:
			return True
		elif self.is_dummy:
			return True
		else:
			#return self.mean-self.std > other.mean+other.std
			return self.mean > other.mean

	def __add__(self, other):
		if other==0 or other is None:
			return self
		elif other.is_dummy:
			return self
		elif self.is_dummy:
			return other
		else:
			return XError(np.concatenate([self.x, other.x], axis=self.dim),
			self.dim,
			self.error_scale,
			self.n_decimals,
			self.mode,
			)

	def __radd__(self, other):
		return self+other

	def __truediv__(self, other):
		self.x = self.x/other
		return self

	def __mul__(self, other):
		self.x = self.x*other
		return self

	def __rmul__(self, other):
		return self.__mul__(other)

	def sum(self):
		return self.x.sum(axis=self.dim)

	def min(self):
		return self.x.min(axis=self.dim)

	def max(self):
		return self.x.max(axis=self.dim)

###################################################################################################################################################

class TopRank():
	def __init__(self, name,
		print_n=10):
		self.name = name
		self.print_n = print_n
		self.names = []
		self.values = []
		self.idxs = None
		
	def add_list(self, names, values):
		for k in range(len(values)):
			self.add(names[k],values[k])

	def add(self, name, value):
		self.names.append(name)
		self.values.append(value)
		
	def calcule_rank(self):
		self.idxs = np.argsort(self.values)[::-1].tolist() # inverse to show high values first
		
	def __len__(self):
		return len(self.names)

	def __repr__(self):
		self.calcule_rank() # just in case
		txt = f'{self.name}[top{self.print_n}]:\n'
		for k,idx in enumerate(self.idxs):
			txt += f'({k+1}) - {self.names[idx]}: {xstr(self.values[idx], n_decimals=4)}\n'
			if k+1>=self.print_n:
				break
		return txt[:-1]

	def get_df(self,
		include_position=True,
		):
		self.calcule_rank() # just in case
		info_dict = {}
		for k,idx in enumerate(self.idxs):
			d = {}
			if include_position:
				d.update({'k':k+1})
			d.update({self.name:self.values[idx]})
			info_dict[self.names[idx]] = d
			if k+1>=self.print_n:
				break
		info_df = pd.DataFrame.from_dict(info_dict, orient='index').reindex(list(info_dict.keys()))
		return info_df

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

def dropout_extreme_percentiles(x,
	p=5,
	mode:str='both',
	):
	if mode=='both':
		valid_indexs = np.where((x>np.percentile(x, p)) & (x<np.percentile(x, 100-p)))
	elif mode=='lower': # dropout lower values
		valid_indexs = np.where(x>np.percentile(x, p))
	elif mode=='upper': # dropout upper values
		valid_indexs = np.where(x<np.percentile(x, 100-p))
	else:
		raise Exception(f'no mode {mode}')
	return x.copy()[valid_indexs], valid_indexs

def get_sigma_clipping_indexing(x, dist_mean, dist_sigma, sigma_m:float,
	apply_lower_bound:bool=True,
	):
	x = np.array(x)
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

def get_random_stratified_keys(keys, keys_classes, class_names, nc):
	'''stratified'''
	d = {c:[] for c in class_names}
	keys = random.sample(keys, len(keys))
	index = 0
	while any([len(d[c])<nc for c in class_names]):
		key = keys[index]
		c = keys_classes[index]
		if len(d[c])<nc:
			d[c].append(key)
		index +=1
	return d