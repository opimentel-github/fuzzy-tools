from __future__ import print_function
from __future__ import division
from . import C_

import numpy as np
from ..strings import xstr
import math

###################################################################################################################################################

def get_max_xerrors(xerrors):
	max_xerrors = []
	max_xerror = max(xerrors)
	for xerror in xerrors:
		#print(max_xerror, xerror)
		assert isinstance(xerror, XError), f'type={type(v)}'

		#if xerror.get_top()>=max_xerror.get_bottom():
		#if xerror.mean>=max_xerror.get_bottom():
		if xerror.mean>=max_xerror.mean:
		#if xerror>=max_xerror:
			max_xerrors += [xerror]
	return [True if v in max_xerrors else False for v in xerrors]

'''def get_max_xerrors(xerrors):
	max_xerrors = []
	rank = sorted(xerrors.copy())[::-1]
	last_v = rank[0]
	for k in range(0, len(rank)):
		v = rank[k]
		assert isinstance(v, XError), f'type={type(v)}'
		if v.get_top()>last_v.get_bottom():
			max_xerrors += [v]
			last_v = v
		else:
			break
	return [True if v in max_xerrors else False for v in xerrors]'''

###################################################################################################################################################

class XError():
	def __init__(self, x,
		dim:int=0,
		error_scale=1,
		n_decimals=C_.N_DECIMALS,
		mode='mean/std',
		repr_pm=True,
		initial_percentiles=[1,5,10,90,95,99],
		):
		self.is_dummy = x is None or len(x)==0
		if self.is_dummy:
			self.x = np.array([])
		else:
			self.x = np.array(x).copy()

		self.dim = dim
		self.error_scale = error_scale
		self.n_decimals = n_decimals
		self.mode = mode
		self.repr_pm = repr_pm
		self.initial_percentiles = initial_percentiles.copy()
		self.reset()

	def reset(self):
		self.percentiles = []
		### calculate statistics
		if not self.is_dummy:
			self.mean = self.get_mean()
			self.median = self.get_median()
			self.std = self.get_std()
			self.serror = self.get_serror()
			
			for p in self.initial_percentiles:
				_ = self.get_percentile(p)

			self.dsymbols = {
				'std':C_.STD_LATEXCHAR,
				'serror':C_.SERROR_LATEXCHAR,
			}

	def item(self):
		assert not self.is_dummy
		assert len(self.x.shape)==1
		assert len(self.x)==1
		return self.x[0]

	def get_percentile(self, p:int):
		assert isinstance(p, int)
		if not p in self.percentiles: # percentile does not exist
			percentile = np.percentile(self.x, p, axis=self.dim)
			setattr(self, f'p{p}', percentile)
			self.percentiles += [p]
		return getattr(self, f'p{p}')

	def get_p(self, p:int):
		return self.get_percentile(p)

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

	def get_shape(self):
		return x.shape

	def __repr__(self):
		if self.is_dummy:
			return f'{xstr(None)}'
		else:
			txt = f'{xstr(self.mean, self.n_decimals)}'
			txt += f'{C_.PM_CHAR}{xstr(self.std, self.n_decimals)}' if self.repr_pm else ''
			return txt

	def get_top(self):
		return -np.inf if self.is_dummy else self.mean+self.std

	def get_bottom(self):
		return np.inf if self.is_dummy else self.mean-self.std

	def get_range(self):
		return self.get_top()-self.get_bottom()

	def __gt__(self, other):
		# is self > other?
		if other==0:
			return self.mean>0
		elif other is None:
			return self.mean>0
		elif other.is_dummy:
			return True
		elif self.is_dummy:
			return False
		else:
			return self.mean > other.mean

	def copy(self,
		x=None,
		):
		xe = XError(self.x.copy() if x is None else x,
			self.dim,
			self.error_scale,
			self.n_decimals,
			self.mode,
			)
		return xe

	def __add__(self, other):
		if isinstance(other, float) or isinstance(other, int):
			xe = self.copy(self.x.copy()+other)
			return xe
		elif isinstance(self, float) or isinstance(self, int):
			xe = other.copy(other.x.copy()+self)
			return xe
		elif other is None:
			return self
		elif other.is_dummy:
			return self
		elif self.is_dummy:
			return other
		else:
			xe = XError(np.concatenate([self.x, other.x], axis=self.dim),
				self.dim,
				self.error_scale,
				self.n_decimals,
				self.mode,
				)
			return xe

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