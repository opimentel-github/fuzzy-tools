from __future__ import print_function
from __future__ import division
from . import _C

import matplotlib.pyplot as plt
import numpy as np
from copy import copy, deepcopy
import scipy.stats as stats

###################################################################################################################################################

def _plot_bar():
	# print(lower_bound, upper_bound)
	pass # fixme

def plot_norm_percentile_bar(ax, _x, _y, std,
	upper_percentile=.95,
	color='k',
	mode='bar',
	alpha=1,
	capsize=0,
	):
	assert upper_percentile>=0 and upper_percentile<=1
	x = copy(_x)
	y = copy(_y)
	norm = stats.norm(loc=y, scale=std)
	lower_bound = norm.ppf(1-upper_percentile) # inverse of cdf # fixme slow
	upper_bound = norm.ppf(upper_percentile) # inverse of cdf
	if mode=='shadow':
		ax.fill_between(x, y-lower_bound, y+upper_bound, facecolor=color, alpha=alpha)
	elif mode=='bar':
		ax.errorbar(x, y, yerr=np.concatenate([y-lower_bound[None], upper_bound[None]-y], axis=0), color=color, capsize=capsize, elinewidth=1, linewidth=0, alpha=alpha)
	else:
		raise Exception(f'invalid mode={mode}')
	return ax

def plot_std_bar(ax, _x, _y, std,
	color='k',
	mode='bar',
	alpha=1,
	capsize=0,
	k=1,
	):
	x = copy(_x)
	y = copy(_y)
	lower_bound = y-std*k
	upper_bound = y+std*k
	if mode=='shadow':
		ax.fill_between(x, y-lower_bound, y+upper_bound, facecolor=color, alpha=alpha)
	elif mode=='bar':
		ax.errorbar(x, y, yerr=np.concatenate([y-lower_bound[None], upper_bound[None]-y], axis=0), color=color, capsize=capsize, elinewidth=1, linewidth=0, alpha=alpha)
	else:
		raise Exception(f'invalid mode={mode}')
	return ax