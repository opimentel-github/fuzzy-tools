from __future__ import print_function
from __future__ import division
from . import _C

import numpy as np
import matplotlib.pyplot as plt
from ..lists import list_product
from ..files import create_dir, PFile
from PIL import Image
import io

VERBOSE = 0
USES_CLOSE_FIG = True
BBOX_INCHES = 'tight'

###################################################################################################################################################

def flat_axs(axs, x, y):
	return [axs[x_,y_] for x_,y_ in list_product(np.arange(0, x),np.arange(0, y))]

###################################################################################################################################################

def close_fig(fig):
	plt.close(fig)
	return

def fig2img(fig):
	if fig is None:
		return None
	buf = io.BytesIO()
	fig.savefig(buf, bbox_inches=BBOX_INCHES, dpi=fig.dpi)
	buf.seek(0)
	img = Image.open(buf)
	return img

def save_fig(fig, save_filedirs,
	uses_close_fig=USES_CLOSE_FIG,
	fig_is_pil_img=False,
	verbose=VERBOSE,
	):
	save_filedirs = [None] if save_filedirs is None else save_filedirs
	if type(save_filedirs)==str:
		save_filedirs = [save_filedirs]

	for k,save_filedir in enumerate(save_filedirs):
		assert type(save_filedir)==str
		save_rootdir = '/'.join(save_filedir.split('/')[:-1])
		create_dir(save_rootdir, verbose=verbose)
		fext = save_filedir.split('.')[-1]

		if fext=='pdf':
			plt.savefig(save_filedir, bbox_inches=BBOX_INCHES)
		elif fext=='png':
			img = fig if fig_is_pil_img else fig2img(fig)
			img.save(save_filedir, format='png')
		else:
			raise Exception(f'fext={fext}')
		if uses_close_fig:
			close_fig(fig)
	return

###################################################################################################################################################

def override(func): return func # tricky
class IFile(PFile):
	def __init__(self, filedir,
		fig=None,
		uses_close_fig=USES_CLOSE_FIG,
		fig_is_pil_img=False,
		):
		super().__init__(filedir,
			fig,
			)
		self.uses_close_fig = uses_close_fig
		self.fig_is_pil_img = fig_is_pil_img

	@override
	def _save(self,
		copy_filedirs=[],
		):
		filedirs = [self.filedir]+copy_filedirs
		save_fig(self.file, filedirs,
			uses_close_fig=self.uses_close_fig,
			fig_is_pil_img=self.fig_is_pil_img,
			verbose=self.verbose,
			)
		self.last_state = 'saved'
		return

	@override
	def _load(self):
		raise Exception('not supported')
		return