from __future__ import print_function
from __future__ import division
from . import _C

import matplotlib
import numpy as np
import imageio
from ..files import create_dir, get_filedirs, delete_filedirs
from .utils import fig2img, save_fig
import os
import math
import matplotlib.pyplot as plt

VERBOSE = 0
AN_SEGS_OFFSET = 1
AN_SAVE_IMAGE_FEXT = 'pdf'
ANIMATION_DURATION = 10
CLOSES_FIG = True

###################################################################################################################################################

class PlotAnimator():
	def __init__(self, save_filedir,
		animation_duration=ANIMATION_DURATION,
		is_dummy:bool=False,
		init_offset:float=AN_SEGS_OFFSET,
		end_offset:float=AN_SEGS_OFFSET,
		save_frames:bool=False,
		saved_frames_fext=AN_SAVE_IMAGE_FEXT,
		verbose=VERBOSE,
		):
		self.save_filedir = save_filedir
		self.animation_duration = animation_duration
		self.is_dummy = is_dummy
		self.init_offset = init_offset
		self.end_offset = end_offset
		self.save_frames = save_frames
		self.saved_frames_fext = saved_frames_fext
		self.verbose = verbose
		self.reset()

	def reset(self):
		self.frames = []

	def __len__(self):
		return len(self.frames)

	def not_dummy(self):
		return not self.is_dummy

	def create_video_from_images(self):
		create_dir('/'.join(self.save_filedir.split('/')[:-1]))
		imgs = [frame for frame in self.frames]
		frame_durations = [self.animation_duration/len(self)]*len(self)

		if self.init_offset>0:
			imgs = [imgs[0]]+imgs
			frame_durations = [self.init_offset]+frame_durations
		
		if self.end_offset>0:
			imgs = imgs+[imgs[-1]]
			frame_durations = frame_durations+[self.end_offset]

		fext = self.save_filedir.split('.')[-1]
		mimsave_kwargs = {
			'duration':frame_durations,
			}
		if fext=='mp4':
			mimsave_kwargs.update({
				'quality':10,
				'pixelformat':'yuv444p', # yuvj444p yuv444p
				'macro_block_size':1, # risking incompatibility
				})
		elif fext=='gif':
			pass
		else:
			raise Exception(f'fext={fext}')

		### save animation
		img_sizes = [img.size for img in imgs]
		assert all([img_size==img_sizes[0] for img_size in img_sizes]), img_sizes
		imageio.mimsave(self.save_filedir, imgs, **mimsave_kwargs)
		print(f'saved in {self.save_filedir}')
		if not matplotlib.__version__=='3.1.3':
			print(f'using {matplotlib.__version__}')

	def append(self, fig,
		closes_fig=CLOSES_FIG,
		):
		if self.not_dummy():
			k = len(self)
			new_save_filedir = '.'.join(self.save_filedir.split('.')[:-1])+f'/{k}.{self.saved_frames_fext}'
			save_fig(fig, new_save_filedir,
				closes_fig=closes_fig,
				)
			img = fig2img(fig)
			self.frames.append(img)
		return

	def save(self,
		reverse:bool=False,
		clean_buffer:bool=True,
		):
		if self.not_dummy():
			if reverse:
				self.reverse_frames()

			self.create_video_from_images()
			if clean_buffer:
				self.clean()

	def clean(self):
		self.reset()

	def reverse_frames(self):
		self.frames.reverse()