from __future__ import print_function
from __future__ import division
from . import _C

from ..datascience import statistics as fstats
from . import colors as cc
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import math
import pandas as pd

PLOT_FIGSIZE = None
DPI = _C.DPI
PERCENTILE = 95
PLOT_GRID_ALPHA = _C.PLOT_GRID_ALPHA
SAMPLES_TEXT = '#'
USES_LOG_SCALE = False
FONTSIZE = 9

###################################################################################################################################################

def plot_bar(plot_df,
	annotations_dict:dict=None,
	bar_width:float=0.7,
	rotate_xlabel:bool=False,
	uses_log_scale:bool=USES_LOG_SCALE,
	uses_legend:bool=True,
	uses_bottom_legend:bool=False, # change for mode
	legend_ncol:int=None,
	add_poblation_annotations:bool=True,
	add_percent_annotations:bool=True,
	xlim_offset_factor=0.2,
	fontsize=FONTSIZE,

	fig=None,
	ax=None,
	figsize:tuple=PLOT_FIGSIZE,
	dpi=DPI,
	xlabel:str='population',
	title:str='plot_bar',
	grid_alpha:float=PLOT_GRID_ALPHA,
	legend_loc:str='upper center',
	cmap=None,
	alpha:float=1,
	**kwargs):
	indexs = list(plot_df.index)
	columns = list(plot_df.columns)
	cmap = cc.get_default_cmap(len(indexs)) if cmap is None else cmap
	fig, ax = plt.subplots(1, 1, figsize=figsize, dpi=dpi) if fig is None else (fig, ax)

	### anotations
	if add_poblation_annotations or add_percent_annotations:
		total_sum = {i:sum([plot_df[c][i] for c in columns]) for i in indexs}
		ann_df = pd.DataFrame.from_dict({c:{i:
			(' '+f'{plot_df[c][i]:,}' if add_poblation_annotations else '')+(f' ({100*plot_df[c][i]/total_sum[i]:.2f}%)' if add_percent_annotations else '')
			 for i in indexs} for c in columns}, orient='columns')

	if uses_log_scale:
		for c in columns:
			plot_df[c] = np.log10(plot_df[c])

	y = np.arange(len(columns))
	legend_handles = []
	maximum_value = 0
	for ki,index in enumerate(indexs):
		list_values = []
		c = cmap.colors[ki]
		legend_handles.append(mpatches.Patch(color=c, label=index))
		new_y = y-bar_width/2.+ki/float(len(indexs))*bar_width
		new_bar_width = bar_width/float(len(indexs))
		for kc,column in enumerate(columns):
			value = plot_df[column][index]
			list_values.append(value)
			maximum_value = max(maximum_value, value)

			if not ann_df is None:
				ann_x = list_values[kc]
				ann_y = new_y[kc] + bar_width/float(len(indexs))/2
				ann = ax.annotate(
						ann_df[column][index],
						xy=(ann_x, ann_y),
						xytext=(0, 0),
						fontsize=fontsize,
						ha='left',
						textcoords='offset points',
						size=fontsize,
						va='center', # center_baseline, baseline, bottom, center, top
						color=c,
					)

		ax.barh(new_y, list_values, height=new_bar_width, align='edge', color=c, alpha=alpha)

	ax.set_yticks(y)
	rotation = 45 if rotate_xlabel else 0
	ha = 'right' if rotate_xlabel else 'right'
	ax.set_yticklabels(columns, rotation=rotation, ha=ha, rotation_mode='anchor')

	#### LEGEND
	if len(indexs)>1 and uses_legend:
		ax.legend(handles=legend_handles)
		if uses_bottom_legend:
			legend_ncol = len(indexs) if legend_ncol is None else legend_ncol
			ax.legend(handles=legend_handles, loc=legend_loc, bbox_to_anchor=(0.5, -0.15), shadow=True, ncol=legend_ncol)	

	if uses_log_scale:
		new_x = np.arange(int(np.min(plot_df.values)), int(np.max(plot_df.values))+2, 1.0)
		ax.set_xticks(new_x)
		ax.set_xticklabels(['$10^{'+str(int(x))+'}$' for x in new_x])

	ax.set_xlim([ax.get_xlim()[0], ax.get_xlim()[1] + ax.get_xlim()[1]*xlim_offset_factor])
	ax.set_axisbelow(True); ax.xaxis.grid(True, alpha=grid_alpha)

	ax.set_xlabel(xlabel)
	ax.set_title(title)
	return fig, ax

def plot_hist_labels(values_dict_raw:dict, classes_names:list,
	bar_width:float=0.5,
	add_percent_annotations:bool=True,
	rotate_xlabel:bool=False,
	uses_log_scale:bool=USES_LOG_SCALE,
	count_scale=1,
	**kwargs):
	'''
	values_dict_raw = set_names: values
	'''
	values_dict = values_dict_raw.copy()
	if not isinstance(values_dict, dict):
		values_dict = {'dataset':values_dict}

	legends = list(values_dict.keys())
	data_dict = {}
	for k,key in enumerate(legends): # the sets
		values = values_dict[key]
		populations_cdict = fstats.get_nof_samples_cdict(values, classes_names)
		for c in populations_cdict.keys():
			if not key in data_dict.keys():
				data_dict[key] = {c:{}}
			data_dict[key][c] = populations_cdict[c]

	plot_df = pd.DataFrame.from_dict(data_dict, orient='index').reindex(list(data_dict.keys()))
	return plot_bar(plot_df,
		bar_width=bar_width,
		rotate_xlabel=rotate_xlabel,
		uses_log_scale=uses_log_scale,
		add_percent_annotations=add_percent_annotations,
		**kwargs)

def plot_hist_discrete(data_dict:dict,
	bar_width:float=0.5,
	uses_bottom_legend:bool=True,
	legend_ncol:int=None,
	uses_density:bool=False,

	fig=None,
	ax=None,
	figsize:tuple=PLOT_FIGSIZE,
	dpi=DPI,
	xlabel:str='values',
	ylabel:str='population',
	title:str='plot_hist_discrete',
	xlim:tuple=[None, None],
	ylim:tuple=[None, None],
	grid:bool=True,
	grid_alpha:float=PLOT_GRID_ALPHA,
	legend_loc:str='upper center',
	cmap=None,
	alpha:float=1,
	verbose:int=0,
	**kwargs):

	fig, ax = (plt.subplots(1,1, figsize=figsize, dpi=dpi) if fig is None else (fig, ax))
	if not isinstance(data_dict, dict):
		data_dict = {'distribution':data_dict} # transform in a dummy dict
	keys = list(data_dict.keys())
	cmap = (cpc.get_default_cmap(len(keys)) if cmap is None else cmap)

	for k,key in enumerate(keys):
		values = data_dict[key]
		uniques, counts = np.unique(values, return_counts=True)
		if uses_density:
			counts_sum = counts.sum()
			counts = [c/counts_sum for c in counts]

		c = cmap.colors[k]
		x = uniques
		new_bar_width = bar_width/float(len(keys))
		new_x = x-bar_width/2. + k/float(len(keys))*bar_width+new_bar_width*0.5
		ax.bar(new_x, counts, width=new_bar_width, color=c, label=key)

	#### LEGEND
	if len(keys) > 1:
		if uses_bottom_legend:
			legend_ncol = (len(keys) if legend_ncol is None else legend_ncol)
			ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), shadow=True, ncol=legend_ncol)
		else:
			ax.legend()

	#### LIMITS
	ax.set_xlim(xlim)
	ax.set_ylim(ylim)
	
	#### OTHER FORMATS
	if grid:
		#xax = ax.set_axisbelow(True); ax.xaxis.grid(True, alpha=grid_alpha)
		yax = ax.set_axisbelow(True); ax.yaxis.grid(True, alpha=grid_alpha)

	ax.set_xlabel(xlabel)
	ax.set_ylabel(ylabel)
	ax.set_title(title)
	return fig, ax

def plot_hist_bins(data_dict:dict,
	bins:int=None,
	linewidth:float=2,
	uses_density:bool=False,
	uses_annotation:bool=True,
	annotation_size:int=9,
	annotation_alpha:float=1,
	histtype:str='step', # step, bar, stepfilled
	return_legend_patches:bool=False,
	lw:float=1.5,
	xrange=None,
	add_bins_title:bool=False,

	fig=None,
	ax=None,
	figsize:tuple=PLOT_FIGSIZE,
	dpi=DPI,
	xlabel:str='values',
	ylabel:str='population',
	title:str='plot_hist_bins',
	xlim:tuple=None,
	ylim:tuple=None,
	grid:bool=True,
	grid_alpha:float=PLOT_GRID_ALPHA,
	legend_loc:str='upper right',
	cmap=None,
	alpha:float=0.5,
	verbose:int=0,
	percentile=PERCENTILE,
	**kwargs):
	if histtype in ['step']:
		alpha=1

	fig, ax = plt.subplots(1, 1, figsize=figsize, dpi=dpi) if fig is None else (fig, ax)
	keys = list(data_dict.keys())
	cmap = cc.get_default_cmap(len(keys)) if cmap is None else cmap

	legend_handles = []
	for k,key in enumerate(keys):
		x = np.array(data_dict[key].copy())
		if verbose>0:
			x_samples, x_mean, x_std, x_min, x_max = len(x), np.mean(x), np.std(x), np.min(x), np.max(x)
			print(f'key: {key}; {SAMPLES_TEXT}: {x_samples:,}; x_mean: {x_mean:.5f}; x_std: {x_std:.5f}; x_min: {x_min:.5f}; x_max: {x_max:.5f}')

		c = cmap.colors[k]
		bins = 'auto' if bins is None else bins
		n, new_bins, patches = ax.hist(x, bins,
			density=uses_density,
			color=c,
			label=None,
			alpha=alpha,
			histtype=histtype,
			range=xrange,
			linewidth=linewidth,
		)
		assert percentile>=0 and percentile<=100
		lower_p = percentile if percentile<50 else 100-percentile
		upper_p = 100-lower_p
		lower_px = np.percentile(x, lower_p)
		median_px = np.percentile(x, 50)
		upper_px = np.percentile(x, upper_p)
		label = f'{key} '+'($p50_{'+str(lower_p)+'}^{'+str(upper_p)+'}='+f'{median_px:.2f}'+'_{'+f'{lower_px:.2f}'+'}^{'+f'{upper_px:.2f}'+'}$; '+f'{len(x):,}#)'
		legend_handles.append(mpatches.Patch(color=c, label=label))

	ax.set_xlabel(xlabel)
	ax.set_ylabel('density' if uses_density and not ylabel is None else ylabel)
	bins_text = f' (bins: {bins:,})' if add_bins_title else ''
	ax.set_title(f'{title}{bins_text}')
	ax.set_xlim([np.min(x), np.max(x)] if xlim is None else xlim)
	ax.set_ylim([None, None] if ylim is None else ylim)
	ax.legend(handles=legend_handles, loc=legend_loc, fontsize=12)

	if grid:
		xax = ax.set_axisbelow(True); ax.xaxis.grid(True, alpha=grid_alpha)
		yax = ax.set_axisbelow(True); ax.yaxis.grid(True, alpha=grid_alpha)

	if uses_annotation:
		magic_offset = 0.15
		max_ylim = ax.get_ylim()[1]
		new_max_ylim = max_ylim*(1+(len(keys))*magic_offset)
		ax.set_ylim([ax.get_ylim()[0], new_max_ylim])

		for k,key in enumerate(keys):
			x = np.array(data_dict[key].copy())
			c = cmap.colors[k]
			ann_y = new_max_ylim*0.9-(k+1)*new_max_ylim*0.1
			#ann = ax.annotate(f'{ann_x:.4f}', xy=(ann_x, ann_y), xytext=(0, annotation_size), fontsize=5, ha='center',
			#		textcoords='offset points',
			#		size=annotation_size, va='center', color='w',
			#		bbox=dict(boxstyle='round', fc=c, ec='none', alpha=annotation_alpha),
			#		#arrowprops=dict(arrowstyle='wedge,tail_width=1.0', fc=c, ec='none', patchA=None, patchB=None, relpos=(0.5, 0.2), alpha=annotation_alpha),
			#		)
			ax.axvline(x=lower_px, ls='--', c=c, label=None, lw=lw)
			ax.axvline(x=median_px, ls='-', c=c, label=None, lw=lw)
			ax.axvline(x=upper_px, ls='--', c=c, label=None, lw=lw)

	if return_legend_patches:
		return fig, ax, legend_handles
	return fig, ax