from __future__ import print_function
from __future__ import division
from . import C_

import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import numpy as np

INTERP_N = 1000
PERCENTILE_PLOT = 95

###################################################################################################################################################

def multiple_lines(ax, xs, ys,
	*args,
	**kwargs,
	):
	for x,y in zip(xs, ys):
		assert x.shape==y.shape
		assert len(x.shape)==1
		ax.plot(x, y, *args, **kwargs)
	return ax

def fill_beetween(ax, xs, ys,
	interp_n=INTERP_N,
	interp_kind='linear',
	percentile=PERCENTILE_PLOT,
	plot_median=True,
	fill_args=[],
	fill_kwargs={},
	median_args=[],
	median_kwargs={},
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
	if percentile is None:
		return multiple_lines(ax, xs, ys, *median_args, **median_kwargs)
	else:
		assert percentile>=0 and percentile<=100
		lower_y = np.nanpercentile(new_ys, 100-percentile, axis=0)
		median_y = np.nanpercentile(new_ys, 50, axis=0)
		upper_y = np.nanpercentile(new_ys, percentile, axis=0)
		ax.fill_between(new_x, lower_y, upper_y, *fill_args, **fill_kwargs)
		if plot_median:
			ax.plot(new_x, median_y, *median_args, **median_kwargs)
	return ax
