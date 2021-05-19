from __future__ import print_function
from __future__ import division
from . import C_

import numpy as np
import matplotlib.pyplot as plt
from ..lists import list_product
from ..files import create_dir

###################################################################################################################################################

def flat_axs(axs, x, y):
	return [axs[x_,y_] for x_,y_ in list_product(np.arange(0, x),np.arange(0, y))]

def close_fig(fig):
	plt.close(fig)

def save_fig(save_filedirs, fig,
	close_fig_after_save=True,
	verbose=1,
	):
	if isinstance(save_filedirs, str):
		save_filedirs = [save_filedirs]
	for k,save_filedir in enumerate(save_filedirs):
		save_fig_(save_filedir, fig,
		close_fig_after_save=False,
		verbose=verbose,
		)
	if close_fig_after_save:
		close_fig(fig)

def save_fig_(save_filedir, fig,
	close_fig_after_save=True,
	verbose=1,
	):
	if not save_filedir is None:
		save_rootdir = '/'.join(save_filedir.split('/')[:-1])
		create_dir(save_rootdir, verbose=verbose)
		plt.savefig(save_filedir)
		if close_fig_after_save:
			close_fig(fig)
	else:
		plt.show()