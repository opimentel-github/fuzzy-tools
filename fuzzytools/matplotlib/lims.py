from __future__ import print_function
from __future__ import division
from . import C_

import matplotlib.pyplot as plt
import numpy as np
from copy import copy, deepcopy

EXTENDED_PERCENT = 0.1

###################################################################################################################################################

def get_xlim(_x_values, axis_extended_percent):
	x_values = np.concatenate(_x_values, axis=0) if isinstance(_x_values, list) else copy(_x_values)
	assert len(x_values.shape)==1

	x_min, x_max = x_values.min(), x_values.max()
	dx = x_max-x_min
	x_margin = axis_extended_percent*dx
	xlim = (x_min-x_margin, x_max+x_margin)
	return xlim

###################################################################################################################################################

class AxisLims(object):
	def __init__(self, axis_clip_values,
		axis_extended_percent=EXTENDED_PERCENT,
		):
		self.axis_clip_values = axis_clip_values
		self.axis_extended_percent = {k:axis_extended_percent for k in axis_clip_values.keys()} if not isinstance(axis_extended_percent, dict) else axis_extended_percent
		self.reset()

	def reset(self):
		self.axis_d = {k:[] for k in self.axis_clip_values.keys()}
		pass

	def append(self, axis_name, axis_value:tuple):
		self.axis_d[axis_name] += [axis_value]

	def get_axis_lim(self, axis_name):
		axis_extended_percent = self.axis_extended_percent[axis_name]
		axis_clip_values = self.axis_clip_values[axis_name]

		axis_lim = get_xlim(self.axis_d[axis_name], axis_extended_percent)
		axis_lim = np.clip(axis_lim, axis_clip_values[0], axis_clip_values[1])
		return axis_lim

	def set_axis_lims(self, ax):
		for k in self.axis_d.keys():
			getattr(ax, f'set_{k}lim')(self.get_axis_lim(k))
		return ax