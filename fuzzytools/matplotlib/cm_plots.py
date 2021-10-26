from __future__ import print_function
from __future__ import division
from . import _C

from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import numpy as np
from ..datascience.xerror import XError
from ..strings import xstr
from copy import copy, deepcopy
import matplotlib as mpl
import pandas as pd
from copy import copy, deepcopy

DPI = _C.DPI
PLOT_FIGSIZE_CMAP = _C.PLOT_FIGSIZE_CMAP
CMAP = plt.cm.Reds
FIGSIZE = (8,8)

###################################################################################################################################################

# def plot_confusion_matrix(y_pred:np.ndarray, y_target:np.ndarray, class_names:list,
# 	new_order_classes:list=None,
# 	normalize_mode:str='true', # None, true, pred
# 	uses_percent:bool=True,
# 	add_accuracy_in_title:bool=0,
# 	fig=None,
# 	ax=None,
# 	figsize=PLOT_FIGSIZE_CMAP,
# 	title='plot_custom_confusion_matrix',
# 	cmap=CMAP,
# 	fontsize=11,
# 	):
# 	assert isinstance(class_names, list)
# 	assert y_pred.shape==y_target.shape
# 	assert y_pred.max()<=len(class_names)
# 	assert y_target.max()<=len(class_names)

# 	cms = confusion_matrix(y_target, y_pred)
# 	return plot_custom_confusion_matrix(cms, class_names,
# 		new_order_classes=new_order_classes,
# 		normalize_mode=normalize_mode,
# 		uses_percent=uses_percent,
# 		add_accuracy_in_title=add_accuracy_in_title,
# 		fig=fig,
# 		ax=ax,
# 		figsize=figsize,
# 		title=title,
# 		cmap=cmap,
# 		fontsize=fontsize,
# 		)

def plot_custom_confusion_matrix(cm,
	fig=None,
	ax=None,
	figsize=FIGSIZE,
	dpi=DPI,
	title='plot_custom_confusion_matrix',
	cmap=CMAP,
	fontsize=11,
	cbar_labelsize=7,
	adds_cbar=False,
	true_label_d={},
	):
	fig, ax = plt.subplots(1, 1, figsize=figsize, dpi=dpi) if fig is None else (fig, ax)
	class_names = cm.get_class_names()
	ax.set(xticks=np.arange(len(class_names)), yticks=np.arange(len(class_names)))
	cm_means = cm.get_means()
	cm_stds = cm.get_stds()
	img = ax.imshow(cm_means,
		interpolation='nearest',
		cmap=cmap,
		)
	boundaries = np.linspace(0, 100, 100//5+1)
	norm = mpl.colors.Normalize(vmin=0, vmax=100)
	if adds_cbar:
		cbar = ax.figure.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax)
		ticks = cbar.get_ticks()
		cbar.set_ticks(ticks)
		cbar.set_ticklabels([f'{t:.0f}%' for t in ticks])
		cbar.ax.tick_params(labelsize=cbar_labelsize)
	ax.set(xlabel='predicted label')
	ax.set(ylabel='true label')
	ax.set(xticklabels=class_names, yticklabels=[f'{c}\n{true_label_d.get(c, "")}' for c in class_names])
	plt.setp(ax.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')

	### set titles
	ax.set_title(title)
	
	### add annotations
	th = cm_means.max()/2.
	for i in range(0, len(class_names)):
		for j in range(0, len(class_names)):
			if cm_means[i,j]<1:
				txt = f'<1%'
			else:
				txt = f'{cm_means[i,j]:.2f}%\n$\\pm${cm_stds[i,j]:.2f}'
			ax.text(j, i, txt,
				ha='center',
				va='center',
				color='white' if cm_means[i,j]>th else 'black',
				fontsize=fontsize,
				)
			
	return fig, ax