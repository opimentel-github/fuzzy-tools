from __future__ import print_function
from __future__ import division
from . import _C

import numpy as np
import matplotlib.pyplot as plt
from . import labels as ds_labels
from ..strings import latex_bf_alphabet_count
from ..dataframes import DFBuilder

FIGSIZE = None
CHECK_DISTRIBUTION = False

###################################################################################################################################################

def plot_misclassification_map(_y_pred_p, _y_true, class_names,
	obj_ids=None,
	check_distribution=CHECK_DISTRIBUTION,
	figsize=FIGSIZE,
	order_mode=None,
	title=None,
	legend_loc='upper right',
	fontsize=10,
	pred_prob_th=None,
	verbose=0,
	dx=.5,
	dx_miss=2,
	also_show_correct_objs_txt=False,
	):
	### checks
	assert len(class_names)>2
	assert obj_ids is None or len(obj_ids)==len(_y_true)
	y_pred_p, y_pred, y_true = ds_labels.format_labels(_y_pred_p, _y_true, class_names,
		check_distribution=check_distribution,
		)

	fig, axs = plt.subplots(len(class_names), 1, figsize=figsize)
	miss_objs_df = DFBuilder()
	for kc,c in enumerate(class_names):
		ax = axs[kc]
		title = ''
		title += f'{latex_bf_alphabet_count(kc)} y_true={c}'+'\n'
		ax.set_title(title[:-1])
		valid_idxs = np.where(y_true==kc)[0]
		# print(valid_idxs)
		pos_x = 0
		for k,idx in enumerate(valid_idxs):
			obj_y_pred = y_pred[idx]
			obj_y_pred_c = class_names[obj_y_pred]
			obj_y_pred_p = y_pred_p[idx][obj_y_pred]
			correct_classification = obj_y_pred==kc
			obj_id = None if obj_ids is None else obj_ids[idx]
			txt = f'{obj_y_pred_c}' if obj_id is None else f'{obj_id} [{obj_y_pred_c}]'
			if correct_classification:
				ax.plot(pos_x, obj_y_pred_p, 'o', c='k')
				if also_show_correct_objs_txt:
					ax.text(pos_x, obj_y_pred_p, txt, rotation=90, ha='center', va='top', fontsize=fontsize)
				pos_x += dx
			else:
				ax.plot(pos_x, obj_y_pred_p, 'D', c='r')
				if pred_prob_th is None or obj_y_pred_p>=pred_prob_th:
					ax.text(pos_x, obj_y_pred_p, txt, rotation=90, ha='center', va='top', fontsize=fontsize)
					if verbose:
						print(f'k={k}; c={c}; obj_y_pred_p={obj_y_pred_p:.3f}; txt={txt}')
				miss_objs_df.append(obj_id, {
					'c':c,
					'obj_y_pred_c':obj_y_pred_c,
					'obj_y_pred_p':obj_y_pred_p,
					})
				pos_x += dx_miss

		ax.plot([None], [None], 'o', c='k', label=f'correct-classification')
		ax.plot([None], [None], 'D', c='r', label=f'miss-classification')
		if not pred_prob_th is None:
			ax.axhline(pred_prob_th, linestyle='--', c='r', label=f'y_pred_threshold={pred_prob_th}')

		ax.set_ylabel('y_pred prob')
		ax.set_ylim([0, 1])
		ax.set_xticks([])
		ax.grid(alpha=.5)
		ax.legend(loc=legend_loc)
	return fig, axs, miss_objs_df.get_df()