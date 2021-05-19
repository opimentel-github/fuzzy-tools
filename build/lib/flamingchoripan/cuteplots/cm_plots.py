from __future__ import print_function
from __future__ import division
from . import C_

from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import numpy as np
from ..datascience.statistics import XError
from ..strings import xstr

###################################################################################################################################################

def reorder_cms_classes(cms, classes, new_order_classes):
	assert len(cms.shape)==3 and cms.shape[1]==cms.shape[2] and cms.shape[1]==len(classes)

	plot_classes = new_order_classes.copy() if not new_order_classes is None else classes.copy()
	plot_classes = list(plot_classes)
	plot_classes_indexs = [plot_classes.index(c) for c in classes]

	cm_y = np.zeros_like(cms) # copy
	new_cms = np.zeros_like(cms) # copy
	for i,ind in enumerate(plot_classes_indexs):
		cm_y[:,ind,:] = cms[:,i,:]
	for i,ind in enumerate(plot_classes_indexs):
		new_cms[:,:,ind] = cm_y[:,:,i]

	return new_cms, plot_classes

###################################################################################################################################################

def plot_confusion_matrix(y_pred:np.ndarray, y_target:np.ndarray, class_names:list,
	new_order_classes:list=None,
	normalize_mode:str='true', # None, true, pred
	uses_percent:bool=True,
	english:bool=True,
	add_accuracy_in_title:bool=True,
	
	fig=None,
	ax=None,
	figsize=C_.PLOT_FIGSIZE_CMAP,
	title:str='plot_custom_confusion_matrix',
	cmap=plt.cm.Reds,
	fontsize=11,
	):
	assert isinstance(class_names, list)
	assert y_pred.shape==y_target.shape
	assert y_pred.max()<=len(class_names)
	assert y_target.max()<=len(class_names)

	cms = confusion_matrix(y_target, y_pred)
	return plot_custom_confusion_matrix(cms, class_names,
		new_order_classes,
		normalize_mode,
		uses_percent,
		english,
		add_accuracy_in_title,
		
		fig,
		ax,
		figsize,
		title,
		cmap,
		fontsize,
		)

def plot_custom_confusion_matrix(cms:np.ndarray, class_names:list,
	new_order_classes:list=None,
	normalize_mode:str='true', # true, pred
	uses_percent:bool=True,
	english:bool=True,
	add_accuracy_in_title:bool=True,
	
	fig=None,
	ax=None,
	figsize=C_.PLOT_FIGSIZE_CMAP,
	title:str='plot_custom_confusion_matrix',
	cmap=plt.cm.Reds,
	fontsize=11,
	):
	'''
	Parameters
	----------
	cms (b,c,c): b=batch of non-norm confusion matrixs
	'''
	### checks
	assert isinstance(cms, np.ndarray) and 'int' in str(cms.dtype), 'must use non-norm confusion matrix for this function'
	assert isinstance(class_names, list)
	assert len(cms.shape)==3 and cms.shape[1]==cms.shape[2] and cms.shape[1]==len(class_names)

	### processing
	cms, plot_classes = reorder_cms_classes(cms, class_names, new_order_classes)
	if normalize_mode=='true':
		cm_norm = cms.astype(np.float32)/(cms.sum(axis=2)[:,:,None])
	elif normalize_mode=='pred':
		cm_norm = cms.astype(np.float32)/(cms.sum(axis=1)[:,None,:])
	else:
		raise Exception(f'no mode {normalize_mode}')

	cms_xe = XError(cm_norm*100, 0)
	fig, ax = plt.subplots(1, 1, figsize=figsize, dpi=C_.PLOT_DPI) if fig is None else (fig, ax)
	ax.set(xticks=np.arange(len(plot_classes)), yticks=np.arange(len(plot_classes)))
	im = ax.imshow(cms_xe.median, interpolation='nearest', cmap=cmap)
	cbar = ax.figure.colorbar(im, ax=ax)
	cbar.ax.set_ylabel('percent [%]')

	ax.set(xlabel='prediction')
	ax.set(ylabel='true label')
	true_class_populations = np.sum(cms[0], axis=-1)
	balanced = all([tcp==true_class_populations[0] for tcp in true_class_populations])
	yticklabels = plot_classes if balanced else [f'{c}\n$N_c={true_class_populations[kc]:,}$' for kc,c in enumerate(plot_classes)]
	ax.set(xticklabels=plot_classes, yticklabels=yticklabels)

	# Rotate the tick labels and set their alignment.
	plt.setp(ax.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')

	### set titles
	if add_accuracy_in_title:
		acc_xe = XError(np.mean(np.diagonal(cm_norm, axis1=1, axis2=2), axis=-1)*100, 0)
		title += f'\n{"" if balanced else "b-"}accuracy: {acc_xe}%'
	ax.set_title(title)
	
	### add annotations
	thresh = cms_xe.median.max()/2.
	for i in range(len(plot_classes)):
		for j in range(len(plot_classes)):
			txt = f'{cms_xe.median[i,j]:.1f}'
			superindex = xstr(cms_xe.p95[i,j]-cms_xe.median[i,j], add_pos=True)
			lowerindex = xstr(cms_xe.p5[i,j]-cms_xe.median[i,j], add_pos=True)
			txt = '${'+txt+'}^{'+superindex+'}_{'+lowerindex+'}$' if len(cms_xe)>1 else txt 
			ax.text(j, i, txt, ha='center', va='center',color='white' if cms_xe.median[i,j]>thresh else 'black', fontsize=fontsize)

	fig.tight_layout()
	return fig, ax