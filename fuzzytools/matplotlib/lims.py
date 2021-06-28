from __future__ import print_function
from __future__ import division
from . import C_

import matplotlib.pyplot as plt
import numpy as np
from copy import copy, deepcopy

EXTENDED_PERCENT = 0.1

###################################################################################################################################################

def get_xlim(_x_values,
	x_extended_percent=EXTENDED_PERCENT,
	):
	x_values = np.concatenate(_x_values, axis=0) if isinstance(_x_values, list) else copy(_x_values)
	assert len(x_values.shape)==1

	x_min, x_max = x_values.min(), x_values.max()
	dx = x_max-x_min
	x_margin = x_extended_percent*dx
	xlim = (x_min-x_margin, x_max+x_margin)
	return xlim

def get_lims(_xy_values,
	x_extended_percent=EXTENDED_PERCENT,
	y_extended_percent=EXTENDED_PERCENT,
	):
	xy_values = np.concatenate(_xy_values, axis=0) if isinstance(_xy_values, list) else copy(_xy_values)
	assert len(xy_values.shape)==2
	assert xy_values.shape[-1]==2

	xlim = get_xlim(xy_values[:,0],
		x_extended_percent,
		)
	ylim = get_xlim(xy_values[:,1],
		y_extended_percent,
		)
	return xlim, ylim

def set_lims(ax, x_values, y_values,
	x_extended_percent=EXTENDED_PERCENT,
	y_extended_percent=EXTENDED_PERCENT,
	):
	xlim, ylim = get_lims(x_values, y_values,)
	ax.set_xlim(xlim)
	ax.set_ylim(ylim)
	return ax