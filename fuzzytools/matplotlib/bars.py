from __future__ import print_function
from __future__ import division
from . import _C

import matplotlib.pyplot as plt
import numpy as np
from copy import copy, deepcopy
import scipy.stats as stats

UPPER_PERCENTILE = 95

###################################################################################################################################################

def plot_std_percentile_bar(ax, _x, _y, std,
	upper_percentile=UPPER_PERCENTILE,
	color='k',
	alpha=1,
	capsize=0,
	):
	### assumes gaussianity
	assert upper_percentile>=0 and upper_percentile<=100
	x = copy(_x)
	y = copy(_y)
	norm = stats.norm(loc=y, scale=std)
	lower_bound = norm.ppf(1-upper_percentile/100) # inverse of cdf # fixme slow
	upper_bound = norm.ppf(upper_percentile/100) # inverse of cdf
	ax.errorbar(x, y, yerr=np.concatenate([y-lower_bound[None], upper_bound[None]-y], axis=0), color=color, capsize=capsize, elinewidth=1, linewidth=0, alpha=alpha)
	return ax

def plot_std_bar(ax, _x, _y, std,
	color='k',
	alpha=1,
	capsize=0,
	std_prop=1,
	):
	x = copy(_x)
	y = copy(_y)
	lower_bound = y-std_prop*std
	upper_bound = y+std_prop*std
	ax.errorbar(x, y, yerr=np.concatenate([y-lower_bound[None], upper_bound[None]-y], axis=0), color=color, capsize=capsize, elinewidth=1, linewidth=0, alpha=alpha)
	return ax