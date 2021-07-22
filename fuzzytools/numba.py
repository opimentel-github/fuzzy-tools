from __future__ import print_function
from __future__ import division
from . import _C

import numpy as np
from numba import jit

###################################################################################################################################################

@jit(nopython=True)
def _concatenate(values, axis):
	return np.concatenate(values, axis)

def concatenate(values, axis=0):
	return _concatenate(tuple(values), axis)

@jit(nopython=True)
def argsort(x):
	return np.argsort(x)

@jit(nopython=True)
def diff_vector(x:np.ndarray,
	uses_prepend=True,
	):
	'''
	x: (l)
	'''
	if len(x)==0:
		return x
	if uses_prepend:
		x0 = np.expand_dims(np.array(x[0]), axis=0)
		nx = np.concatenate((x0, x), axis=0)
		return nx[1:] - nx[:-1]
	else:
		return x[1:] - x[:-1]

@jit(nopython=True)
def copy(x:np.ndarray):
	return x.copy()

@jit(nopython=True)
def bernoulli(p, size):
	r = np.random.binomial(p=p, n=1, size=size)
	r = r.astype(np.bool_)
	return r

@jit(nopython=True) # slower????
def normal(mu, std):
	standar_r = np.random.standard_normal(size=mu.shape)
	return mu+standar_r*std # reparametrization trick

@jit(nopython=True)
def uniform(a, b, size):
	r = np.random.uniform(a, b, size=size)
	return r

@jit(nopython=True)
def log(x,
	eps=_C.EPS,
	):
	assert np.all(x>=0)
	return np.log(x+eps)

###################################################################################################################################################
### NOT SURE IF THE FOLLOWING WORTH IT

#@jit(nopython=True)
def min(x,
	axis=0,
	):
	return x.min(axis=axis)

#@jit(nopython=True)
def argmin(x,
	axis=0,
	):
	return x.argmin(axis=axis)

#@jit(nopython=True)
def max(x,
	axis=0,
	):
	return x.max(axis=axis)

#@jit(nopython=True)
def argmax(x,
	axis=0,
	):
	return x.argmax(axis=axis)


@jit(nopython=True)
def log_mu_std(x,
	eps=_C.EPS,
	axis=-1,
	):
	assert np.all(x>=0) # slow
	log_x = np.log(x+eps)
	mu = np.mean(log_x, axis=axis)
	std = np.std(log_x, axis=axis)
	return mu, std

@jit(nopython=True)
def log_norm(x, mu, std,
	eps=_C.EPS,
	):
	assert np.all(x>=0) # slow
	log_x = np.log(x+eps)
	z = (log_x-mu)/(std+eps)
	return z

@jit(nopython=True)
def inv_log_norm(z, mu, std,
	eps=_C.EPS,
	):
	log_x = z*(std+eps)+mu
	x = np.exp(log_x)-eps
	return x