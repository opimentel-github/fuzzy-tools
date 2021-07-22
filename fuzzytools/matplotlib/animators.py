from __future__ import print_function
from __future__ import division
from . import _C

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy as np
import imageio
from ..files import create_dir, get_filedirs, delete_filedirs
from .utils import _fig2img, save_fig
import os
import math
import matplotlib.pyplot as plt

###################################################################################################################################################

class PlotAnimator():
	def __init__(self,
		video_duration=10,
		is_dummy:bool=False,
		init_offset:float=_C.AN_SEGS_OFFSET,
		end_offset:float=_C.AN_SEGS_OFFSET,
		save_init_frame:bool=False,
		save_end_frame:bool=False,
		verbose=_C.VERBOSE,
		):
		self.video_duration = video_duration
		self.is_dummy = is_dummy
		self.init_offset = init_offset
		self.end_offset = end_offset
		self.save_init_frame = save_init_frame
		self.save_end_frame = save_end_frame
		self.verbose = verbose
		self.reset()

	def reset(self):
		self.frames = []

	def __len__(self):
		return len(self.frames)

	def not_dummy(self):
		return not self.is_dummy

	def get_fps(self):
		return len(self)/self.video_duration

	def create_video_from_images(self, save_filedir:str):
		imgs = [i for i in self.frames]
		fps = self.get_fps()
		create_dir('/'.join(save_filedir.split('/')[:-1]))

		if self.init_offset>0:
			imgs = [imgs[0]]*math.ceil(self.init_offset*fps) + imgs
		
		if self.end_offset>0:
			imgs = imgs + [imgs[-1]]*math.ceil(self.end_offset*fps)

		fext = save_filedir.split('.')[-1]
		mimsave_kwargs = {
			'fps':fps,
			}
		if fext=='mp4':
			mimsave_kwargs.update({
				'quality':10,
				#'codec':'mjpeg', # libx264 mjpeg
				'pixelformat':'yuv444p', # yuvj444p yuv444p
				'macro_block_size':1, # risking incompatibility
				})
		elif fext=='gif':
			mimsave_kwargs.update({
				'fps':fps,
				#'codec':'mjpeg', # libx264 mjpeg
				})
		img_sizes = [img.size for img in imgs]
		assert all([img_size==img_sizes[0] for img_size in img_sizes]), img_sizes
		imageio.mimsave(save_filedir, imgs, **mimsave_kwargs)

		save_filename = '.'.join(save_filedir.split('.')[:-1])
		if self.save_init_frame:
			save_fig(f'{save_filename}.first.{_C.AN_SAVE_IMAGE_FEXT}', imgs[0],
				uses_close_fig=None,
				verbose=self.verbose,
				fig_is_img=True,
				)

		if self.save_end_frame:
			save_fig(f'{save_filename}.last.{_C.AN_SAVE_IMAGE_FEXT}', imgs[-1],
				uses_close_fig=None,
				verbose=self.verbose,
				fig_is_img=True,
				)

	def append(self, fig,
		uses_close_fig=True,
		):
		if self.not_dummy():
			img = _fig2img(fig, uses_close_fig)
			self.frames.append(img)
			return
		return

	def save(self, save_filedir:str,
		reverse:bool=False,
		clean_buffer:bool=True,
		):
		if self.not_dummy():
			if reverse:
				self.reverse_frames()

			self.create_video_from_images(save_filedir)
			if clean_buffer:
				self.clean()

	def clean(self):
		self.reset()
		#delete_filedirs([f'{self.temp_filedir}.png'], verbose=0)

	def reverse_frames(self):
		self.frames.reverse()