from __future__ import print_function
from __future__ import division
from . import _C

import numpy as np
import math
from copy import copy, deepcopy
from .. import strings
import math

N_DECIMALS = _C.N_DECIMALS
PM_CHAR = _C.PM_CHAR
INITIAL_PERCENTILES = [1, 5, 10, 90, 95, 99]

###################################################################################################################################################

def mean_std_repr(mean, std, n_decimals):
	mean_txt = strings.xstr(mean,
		n_decimals=n_decimals,
		)
	std_txt = strings.xstr(std,
		n_decimals=n_decimals,
		)
	txt = f'{mean_txt}{PM_CHAR}{std_txt}'
	return txt

###################################################################################################################################################

class XError():
	def __init__(self, _x,
		dim:int=0, # fixme
		error_scale=1,
		n_decimals=N_DECIMALS,
		mode='mean/std',
		repr_pm=True,
		initial_percentiles=INITIAL_PERCENTILES,
		):
		self._x = _x
		self.dim = dim
		self.error_scale = error_scale
		self.n_decimals = n_decimals
		self.mode = mode
		self.repr_pm = repr_pm
		self.initial_percentiles = initial_percentiles
		self.reset()

	def reset(self):
		is_dummy = self._x is None or len(self._x)==0
		self.x = np.array([]) if is_dummy else np.array(self._x).copy()
		self.shape = self.x.shape
		self.compute_statistics()
		return self

	def compute_statistics(self):
		if not self.is_dummy():
			self.percentiles = []
			self.mean = self.get_mean()
			self.median = self.get_median()
			self.std = self.get_std()
			self.serror = self.get_standar_error()
			for p in self.initial_percentiles:
				self.get_percentile(p)

	def is_dummy(self):
		return len(self.x)==0

	def get_size(self):
		return self.shape

	def is_1d(self):
		return len(self.shape)==1

	def get_raw_repr(self,
		name='x',
		):
		return strings.get_raw_numpy_repr(self.x, name=name)

	# def __getitem__(self, idx):
	# 	# avoid this if you want dataframe repr working!
	# 	return self.get_item(idx)

	def get_item(self, idx):
		if self.is_dummy():
			return None
		elif self.is_1d():
			return self.x[idx]
		else:
			return np.take(self.x, [idx], axis=self.dim)

	def get_percentile(self, p:int):
		assert p>=0 and p<=100
		assert type(p)==int
		if not p in self.percentiles: # percentile does not exist
			percentile = np.percentile(self.x, p, axis=self.dim)
			setattr(self, f'p{p}', percentile)
			self.percentiles += [p]
		return getattr(self, f'p{p}')

	def get_p(self, p:int):
		return self.get_percentile(p)

	def get_pbounds(self, p):
		if p<=50:
			return self.get_p(p), self.get_p(100-p)
		else:
			return self.get_p(100-p), self.get_p(p)

	def get_mean(self):
		return np.mean(self.x, axis=self.dim)

	def get_median(self):
		return self.get_p(50)

	def get_std(self):
		std = np.std(self.x, axis=self.dim)*self.error_scale
		return std

	def set_repr_pm(self, repr_pm):
		self.repr_pm = repr_pm
		return self

	def get_standar_error(self):
		'''
		Standar Error = sqrt(sum((x-x_mean)**2)/(N-1)) / sqrt(N)
		'''
		if len(self)>1:
			return np.std(self.x, axis=self.dim, ddof=1)/math.sqrt(self.x.shape[self.dim])*self.error_scale
		else:
			return self.get_std()

	def __len__(self):
		return self.x.shape[self.dim]

	def __repr__(self):
		if self.is_dummy():
			return f'{strings.xstr(None)}'
		else:
			txt = mean_std_repr(self.get_mean(), self.get_std(), self.n_decimals) if self.repr_pm else ''
			return txt

	def copy(self):
		return copy(self)

	def __copy__(self):
		xe = XError(self.x.copy(),
			self.dim,
			self.error_scale,
			self.n_decimals,
			self.mode,
			)
		return xe

	def __add__(self, other):
		if self is None or self==0:
			return copy(other)

		elif other is None or other==0:
			return copy(self)

		elif type(self)==XError and type(other)==XError:
			if self.is_dummy():
				return copy(other)

			if other.is_dummy():
				return copy(self)

			xe = copy(self)
			xe._x = np.concatenate([self.x, other.x], axis=self.dim)
			return xe.reset()

		elif type(self)==float or type(self)==int:
			xe = copy(other)
			xe._x = other.x+self
			return xe.reset()

		elif type(other)==float or type(other)==int:
			xe = copy(self)
			xe._x = self.x+other
			return xe.reset()

		else:
			raise Exception(f'{type(self)}; {type(other)}')

	def __radd__(self, other):
		return self+other

	def __truediv__(self, other):
		assert type(other)==float or type(other)==int
		xe = copy(self)
		xe._x = xe._x/other
		return xe.reset()

	def __mul__(self, other):
		assert type(other)==float or type(other)==int
		xe = copy(self)
		xe._x = xe._x*other
		xe.reset()
		return xe

	def __rmul__(self, other):
		return self*other

	def sum(self):
		return self.x.sum(axis=self.dim)

	def min(self):
		return self.x.min(axis=self.dim)

	def max(self):
		return self.x.max(axis=self.dim)