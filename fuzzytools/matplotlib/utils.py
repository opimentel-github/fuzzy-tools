from __future__ import print_function
from __future__ import division
from . import _C

import numpy as np
import matplotlib.pyplot as plt
from ..lists import list_product
from ..files import create_dir, PFile
from PIL import Image
import io

###################################################################################################################################################

def flat_axs(axs, x, y):
	return [axs[x_,y_] for x_,y_ in list_product(np.arange(0, x),np.arange(0, y))]

###################################################################################################################################################

def close_fig(fig):
	plt.close(fig)
	return

'''
def _fig2img(fig,
	uses_close_fig=True,
	):
	img = Image.frombytes('RGB', fig.canvas.get_width_height(), fig.canvas.tostring_rgb())
	if uses_close_fig:
		close_fig(fig)
	return img
'''

def _fig2img(fig,
	uses_close_fig=True,
	):
	if fig is None:
		return None
	buf = io.BytesIO()
	fig.savefig(buf, bbox_inches='tight')
	buf.seek(0)
	img = Image.open(buf)
	if uses_close_fig:
		close_fig(fig)
	return img

def save_fig(save_filedirs, fig,
	uses_close_fig=True,
	verbose=_C.VERBOSE,
	fig_is_img=False,
	):
	save_filedirs = [None] if save_filedirs is None else save_filedirs
	if isinstance(save_filedirs, str):
		save_filedirs = [save_filedirs]

	img = fig if fig_is_img else _fig2img(fig, uses_close_fig)

	for k,save_filedir in enumerate(save_filedirs):
		assert isinstance(save_filedir, str)
		save_rootdir = '/'.join(save_filedir.split('/')[:-1])
		create_dir(save_rootdir, verbose=verbose)
		img.save(save_filedir, format='png')
	return

###################################################################################################################################################

def override(func): return func # tricky
class IFile(PFile):
	def __init__(self, filedir,
		fig=None,
		uses_close_fig=True,
		):
		img = _fig2img(fig, uses_close_fig)
		super().__init__(filedir,
			img,
			)

	@override
	def _save(self,
		copy_filedirs=[],
		):
		filedirs = [self.filedir]+copy_filedirs
		save_fig(filedirs, self.file,
			None,
			self.verbose,
			True,
			)
		self.last_state = 'saved'
		return

	@override
	def _load(self):
		raise Exception('not supported')
		return