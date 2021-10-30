from __future__ import print_function
from __future__ import division
from . import _C

import sys
import re
from tqdm import tqdm
from . import strings
from . import ipynb
from .times import get_date_hour

BAR_FORMAT = '{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}, {rate_fmt}{postfix}]'
#'bar_format':'{l_bar}{bar}| {n_fmt}/{total_fmt} [{rate_fmt}{postfix}]',
#'bar_format':'{l_bar}{bar}{r_bar}',
#'bar_format':'{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]',
BAR_FULL_MODE = '%(current)d/%(total)d %(bar)s %(percent)3d%% - %(remaining)d remaining - %(string)s'
BAR_OUTPUT = sys.stderr # sys.stderr sys.stdout
WIDTH = 30

###################################################################################################################################################

class ProgressBarMulti():
	def __init__(self, total:int, m:int,
		width:int=WIDTH,
		fmt=BAR_FULL_MODE,
		output=BAR_OUTPUT,
		):
		self.bar_names = [k for k in range(m)]
		self.bar = ProgressBarMultiColor(total, self.bar_names,
			None,
			width,
			fmt,
			output,
			)

	def __call__(self, texts:list,
		update:bool=True,
		):
		assert isinstance(texts, list)
		tdict = {n:texts[kn] for kn,n in enumerate(self.bar_names)}
		self.bar(tdict, update)
			
	def done(self):
		self.bar.done()

###################################################################################################################################################

class ProgressBarMultiColor():
	def __init__(self, total:int, bar_names:list,
		bar_colors:list=None,
		width:int=WIDTH,
		fmt=BAR_FULL_MODE,
		output=BAR_OUTPUT,
		):
		self.in_ipynb = ipynb.in_ipynb()
		self.bar_names = bar_names.copy()
		self.bar_colors = [None]*len(self.bar_names) if bar_colors is None else bar_colors.copy()
		self.bars = {}
		for kc,c in enumerate(bar_names):
			bar = ProgressBar(total,
				width,
				fmt,
				output,
				position=kc,
				)
			self.bars[c] = bar
			if self.in_ipynb:
				break

	def __call__(self, tdict:dict,
		update:bool=True,
		):
		assert isinstance(tdict, dict)

		if self.in_ipynb:
			txts = [strings.color_str(tdict.get(n, ''), self.bar_colors[kn]) for kn,n in enumerate(self.bar_names)]
			txt = ''.join(txts)
			self.bars[self.bar_names[0]](txt, update)

		else:
			lengths = [len(tdict[key]) for key in tdict.keys()]
			extra_chars = {n:max(lengths)-len(tdict.get(n, '')) for n in self.bar_names}
			for kn,n in enumerate(self.bar_names):
				txt = strings.color_str(tdict.get(n, ''), self.bar_colors[kn])
				txt += ' '*extra_chars[n]
				self.bars[n](txt, update)
			
	def done(self):
		for key in self.bars.keys():
			self.bars[key].done()

###################################################################################################################################################

class ProgressBar():
	def __init__(self, total:int,
		width:int=WIDTH,
		fmt=BAR_FULL_MODE,
		output=BAR_OUTPUT,
		position:int=0,
		dynamic_ncols=False,
		bar_format=BAR_FORMAT,
		miniters=1.,
		append_time=False,
		dummy=False,
		):
		self.total = total
		self.width = width
		self.fmt = fmt
		self.output = output
		self.position = position
		self.dynamic_ncols = dynamic_ncols
		self.bar_format = bar_format
		self.miniters=miniters
		self.append_time = append_time
		self.dummy = dummy
		self.reset()

	def reset(self):
		if self.not_dummy():
			self._done = False
			self.bar_kwargs = {
				'bar_format':self.bar_format,
				'postfix':'',
				'total':self.total,
				'file':self.output,
				'position':self.position,
				'leave':True,
				'dynamic_ncols':self.dynamic_ncols,
				'miniters':self.miniters,
				}

	def not_dummy(self):
		return not self.dummy

	def __call__(self,
		txt:str='???',
		update:bool=True,
		):
		assert isinstance(txt, str)
		if self.not_dummy():
			if not hasattr(self, '_bar'):
				self._bar = tqdm(**self.bar_kwargs)

			if self.append_time:
				date, hour = get_date_hour()
				txt += f'[{hour}]'
			
			self._bar.set_postfix_str(txt)
			#d.set_description(d)
			if update:
				self._bar.update()
			return

	def __repr__(self):
		return str(self._bar)
	
	def get_bar(self):
		if hasattr(self, '_bar'):
			return self._bar
		else:
			return None

	def done(self):
		if self.not_dummy():
			if not self._done and hasattr(self, '_bar'):
				self._bar.close()
			return

	def close(self):
		self.done()
		return