from __future__ import print_function
from __future__ import division
from . import C_

import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import numpy as np

INTERP_N = 1000

###################################################################################################################################################

def plot_multiple_lines(ax, xs, ys,
	*args,
	**kwargs,
	):
	for x,y in zip(xs, ys):
		assert x.shape==y.shape
		assert len(x.shape)==1
		ax.plot(x, y, *args, **kwargs)
	return ax

def plot_fill_beetween(ax, xs, ys,
	interp_n=INTERP_N,
	interp_kind='linear',
	*args,
	**kwargs,
	):
	x_min = min([x.min() for x in xs])
	x_max = max([x.max() for x in xs])
	new_x = np.linspace(x_min, x_max, interp_n)
	new_ys = []
	for x,y in zip(xs, ys):
		assert x.shape==y.shape
		assert len(x.shape)==1
		new_y = interp1d(x, y, kind=interp_kind, bounds_error=False)(new_x)
		new_ys += [new_y[None]]
	
	new_ys = np.concatenate(new_ys, axis=0)
	ax.fill_between(new_x, np.nanmin(new_ys, axis=0), np.nanmax(new_ys, axis=0), *args, **kwargs)
	return ax
