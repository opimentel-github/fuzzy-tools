from __future__ import print_function
from __future__ import division
from . import _C

import numpy as np
from ..strings import xstr
import math
from copy import copy
from scipy import stats

###################################################################################################################################################

#class NDXError():

class XError():
	def __init__(self, _x,
		dim:int=0, # fixme
		error_scale=1,
		n_decimals=_C.N_DECIMALS,
		mode='mean/std',
		repr_pm=True,
		initial_percentiles=[1,5,10,90,95,99],
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

	def compute_statistics(self):
		#print('compute_statistics')
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

	def size(self):
		return self.shape

	def is_1d(self):
		return len(self.shape)==1

	def item(self, idx):
		if self.is_dummy():
			return None
		elif self.is_1d():
			return self.x[idx]
		else:
			return np.take(self.x, [idx], axis=self.dim)

	def get_percentile(self, p:int):
		assert p>=0 and p<=100
		assert isinstance(p, int)
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
			return f'{xstr(None)}'
		else:
			txt = f'{xstr(self.mean, self.n_decimals)}'
			txt += f'{_C.PM_CHAR}{xstr(self.std, self.n_decimals)}' if self.repr_pm else ''
			return txt

	def __ge__(self, other): # self >= other
		if other is None or other.is_dummy():
			return True
		elif self is None or self.is_dummy():
			return False
		else:
			return self>other or self==other

	def __eq__(self, other): # self == other
		if other is None or other.is_dummy():
			return self is None or self.is_dummy()
		elif self is None or self.is_dummy():
			return other is None or other.is_dummy()
		else:
			return np.allclose(self.mean, other.mean)

	def __gt__(self, other): # self > other
		if other is None or other.is_dummy():
			return True
		elif self is None or self.is_dummy():
			return False
		else:
			return self.mean>other.mean

	def gt_ttest(self, other,
		pvalue_th=0.05,
		verbose=0,
		):
		assert len(self)>1
		assert len(other)>1
		tvalue, pvalue = stats.ttest_ind(self.x, other.x, axis=self.dim)
		is_greater = self.mean>other.mean and pvalue<pvalue_th
		if verbose:
			print(f'{str(self)}>{str(other)}={is_greater} (pvalue={pvalue}, th={pvalue_th})')
		return is_greater

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
		if isinstance(other, float) or isinstance(other, int):
			#xe = self.copy(self.x.copy()+other)
			xe = copy(self)
			xe._x = self.x+other
			xe.reset()
			return xe

		elif isinstance(self, float) or isinstance(self, int):
			xe = copy(other)
			xe._x = other.x+self
			xe.reset()
			return xe

		elif other is None or other.is_dummy():
			return copy(self)

		elif self is None or self.is_dummy():
			return copy(other)

		else:
			xe = copy(self)
			xe._x = np.concatenate([self.x, other.x], axis=self.dim)
			xe.reset()
			return xe

	def __radd__(self, other):
		return self+other

	def __truediv__(self, other):
		assert isinstance(other, float) or isinstance(other, int)
		xe = copy(self)
		xe._x = xe._x/other
		xe.reset()
		return xe

	def __mul__(self, other):
		assert isinstance(other, float) or isinstance(other, int)
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