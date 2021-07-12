from __future__ import print_function
from __future__ import division
from . import C_

import numpy as np
import matplotlib.pyplot as plt
from . import labels as ds_labels

FIGSIZE = None
CHECK_DISTRIBUTION = False

###################################################################################################################################################

def plot_missclassifications(_y_pred_p, _y_true, class_names,
	obj_ids=None,
	check_distribution=CHECK_DISTRIBUTION,
	figsize=FIGSIZE,
	order_mode=None,
	title=None,
	legend_loc='upper right',
	fontsize=10,
	pred_prob_th=None,
	):
	### checks
	assert len(class_names)>2
	assert obj_ids is None or len(obj_ids)==len(_y_true)
	y_pred_p, y_pred, y_true = ds_labels.format_labels(_y_pred_p, _y_true, class_names,
		check_distribution=check_distribution,
		)

	fig, axs = plt.subplots(len(class_names), 1, figsize=figsize)
	for kc,c in enumerate(class_names):
		ax = axs[kc]
		valid_idxs = np.where(y_true==kc)[0]
		# print(valid_idxs)
		for k,idx in enumerate(valid_idxs):
			obj_y_pred = y_pred[idx]
			obj_y_pred_c = class_names[obj_y_pred]
			obj_y_pred_p = y_pred_p[idx][obj_y_pred]
			correct_classification = obj_y_pred==kc
			obj_id = None if obj_ids is None else obj_ids[idx]
			if correct_classification:
				ax.plot(k, obj_y_pred_p, 'o', c='k')
			else:
				ax.plot(k, obj_y_pred_p, 'D', c='r')
				if pred_prob_th is None or obj_y_pred_p>=pred_prob_th:
					txt = f'{obj_y_pred_c}' if obj_id is None else f'{obj_id} [{obj_y_pred_c}]'
					ax.text(k, obj_y_pred_p, txt, rotation=90, ha='center', va='top', fontsize=fontsize)

		ax.plot([None], [None], 'o', c='k', label=f'correct-classification for y_true={c}')
		ax.plot([None], [None], 'D', c='r', label=f'miss-classification for y_true={c}')
		if not pred_prob_th is None:
			ax.axhline(pred_prob_th, linestyle='--', c='r', label=f'y_pred_threshold={pred_prob_th}')

		ax.set_ylabel('y_pred prob')
		ax.set_ylim([0, 1])
		ax.set_xticks([])
		ax.grid(alpha=.5)
		ax.legend(loc=legend_loc)
	
	axs[0].set_title(title)
	return fig, axs