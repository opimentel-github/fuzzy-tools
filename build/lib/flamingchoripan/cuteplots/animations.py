from __future__ import print_function
from __future__ import division
from . import C_

from ..progress_bars import ProgressBar
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy as np
import imageio
from ..files import create_dir, get_filedirs
import os
import math

'''
def create_video_from_images_disk(load_rootdir:str, save_rootdir:str,
	delete_files:bool=False,
	):
	filedirs = get_filedirs(load_rootdir, LOAD_IMAGEFORMAT) # load filenames from load_folder
	filedirs = sorted(filedirs)
	print(f'filedirs: {len(filedirs)}')
	assert len(filedirs)>0, 'no images'
		
	images = []
	for filedir in filedirs:
		image = imageio.imread(filedir, pilmode='RGB')
		images.append(image)
		if delete_files:
			os.remove(filedir) # REMOVE!!!
	
	create_video_from_images(images, save_rootdir, save_cfilename)
'''

def create_video_from_images(raw_images:list, save_rootdir:str, save_cfilename:str,
	fps:int=15,
	video_fext:str=C_.AN_VIDEO_FEXT,
	save_first_frame:bool=True,
	save_last_frame:bool=True,
	init_offset:float=C_.AN_SEGS_OFFSET,
	end_offset:float=C_.AN_SEGS_OFFSET,
	):
		
	images = raw_images.copy()
	save_filedir = f'{save_rootdir}/{save_cfilename}.{video_fext}'
	print(f'creating video in: {save_filedir}')
	create_dir(save_rootdir)

	if init_offset>0:
		images = [images[0]]*math.ceil(init_offset*fps) + images
	
	if end_offset>0:
		images = images + [images[-1]]*math.ceil(end_offset*fps)

	imageio.mimsave(save_filedir, images, fps=fps, quality=C_.AN_VIDEO_QUALITY)#, codec='mjpeg')

	if save_first_frame:
		save_filedir = f'{save_rootdir}/{save_cfilename}.first.{C_.AN_SAVE_IMAGE_FEXT}'
		imageio.imsave(save_filedir, images[0])

	if save_last_frame:
		save_filedir = f'{save_rootdir}/{save_cfilename}.last.{C_.AN_SAVE_IMAGE_FEXT}'
		imageio.imsave(save_filedir, images[-1])

class PlotAnimation():
	def __init__(self, N_images:int, fps:int,
		dummy:bool=False,
		video_fext:str=C_.AN_VIDEO_FEXT,
		init_offset:float=C_.AN_SEGS_OFFSET,
		end_offset:float=C_.AN_SEGS_OFFSET,
		):
		setattr(self, 'N_images', N_images)
		setattr(self, 'fps', fps)
		setattr(self, 'dummy', dummy)
		setattr(self, 'video_fext', video_fext)
		setattr(self, 'init_offset', init_offset)
		setattr(self, 'end_offset', end_offset)
		setattr(self, 'frames', [])

		if self.dummy:
			print('PlotAnimation is dummy')
		else:
			if not self.N_images is None and self.N_images>0:
				self.bar = ProgressBar(N_images)

	def add_frame(self, fig):
		if not self.dummy:
			if not self.N_images is None and self.N_images>0:
				self.bar(f'{len(self.frames)}')
			canvas = FigureCanvas(fig)
			#canvas.draw() # ugly
			#canvas.draw_idle()
			canvas.print_figure('temp/temp')
			image = np.fromstring(canvas.tostring_rgb(), dtype='uint8')
			new_shape = canvas.get_width_height()[::-1] + (3,)
			#print(new_shape)
			image = image.reshape(new_shape)
			self.frames.append(image)
			#fig.clear()

	def save(self, video_save_rootdir:str, video_save_cfilename:str,
		reverse:bool=False,
		clean_buffer:bool=True,
		):
		if not self.dummy:
			self.bar.done()
			if reverse:
				self.reverse_frames()

			kwargs = {
				'fps':self.fps,
				'video_fext':self.video_fext,
				'init_offset':self.init_offset,
				'end_offset':self.end_offset,
			}
			create_video_from_images(self.frames, video_save_rootdir, video_save_cfilename, **kwargs)
			if clean_buffer:
				print('cleaning buffer')
				self.frames = [] # CLEAN

	def reverse_frames(self):
		self.frames.reverse()