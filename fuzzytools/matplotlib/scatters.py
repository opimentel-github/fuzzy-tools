from __future__ import print_function
from __future__ import division
from . import _C

import matplotlib.pyplot as plt
from copy import copy, deepcopy
import numpy as np
from ..datascience import labels as ds_labels

###################################################################################################################################################

def scatter(ax, x, _y_true, class_names, scatter_kwargs,
	sort_by_count=True,
	add_class_label=True,
	):
	### checks
	assert len(x.shape)==2
	assert x.shape[-1]==2
	assert len(x)==len(_y_true)

	_, _, y_true = ds_labels.format_labels(None, _y_true, class_names)
	y_uniques, counts = np.unique(y_true, return_counts=True)
	plot_order = np.argsort(counts)[::-1] if sort_by_count else list(range(0, len(y_uniques)))
	assert len(y_uniques)==len(class_names)
	
	for k in plot_order:
		y_unique = y_uniques[k]
		count = counts[k]
		class_name = class_names[k]
		if count==0:
			continue
		valid_idxs = np.where(y_true==y_unique)[0]
		_x = x[valid_idxs]
		_y_true = [valid_idxs]
		_scatter_kwargs = deepcopy(scatter_kwargs[class_name])
		if add_class_label:
			label = _scatter_kwargs.get('label', None)
			_scatter_kwargs.update({
				'label':f'{class_name}' if label is None else f'{label} [{class_name}]',
				})
		ax.scatter(_x[:,0], _x[:,1], **_scatter_kwargs)
	return ax