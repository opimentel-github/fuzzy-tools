from __future__ import print_function
from __future__ import division
from . import C_

import sys
import re
from tqdm import tqdm
from . import strings
from . import ipynb

###################################################################################################################################################

class ProgressBarMulti():
	def __init__(self, total:int, m:int,
		width:int=40,
		fmt=C_.BAR_FULL_MODE,
		symbol:str=C_.BAR_CHAR,
		output=C_.DEFAULT_PRINT_OUTPUT,
		):
		self.bar_names = [k for k in range(m)]
		self.bar = ProgressBarMultiColor(total, self.bar_names,
			None,
			width,
			fmt,
			symbol,
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

class ProgressBarMultiColor():
	def __init__(self, total:int, bar_names:list,
		bar_colors:list=None,
		width:int=40,
		fmt=C_.BAR_FULL_MODE,
		symbol:str=C_.BAR_CHAR,
		output=C_.DEFAULT_PRINT_OUTPUT,
		):
		self.in_ipynb = ipynb.in_ipynb()
		self.bar_names = bar_names.copy()
		self.bar_colors = [None]*len(self.bar_names) if bar_colors is None else bar_colors.copy()
		self.bars = {}
		for kc,c in enumerate(bar_names):
			bar = ProgressBar(total,
				width,
				fmt,
				symbol,
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

class ProgressBar():
	def __init__(self, total:int,
		width:int=40,
		fmt=C_.BAR_FULL_MODE,
		symbol:str=C_.BAR_CHAR,
		output=C_.DEFAULT_PRINT_OUTPUT,
		position:int=0,
		dynamic_ncols:bool=True,
		):
		bar_kwargs = {
			#'bar_format':'{l_bar}{bar}{r_bar}',
			#'bar_format':'{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]',
			'bar_format':'{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}, {rate_fmt}{postfix}]',
			#'bar_format':'{l_bar}{bar}| {n_fmt}/{total_fmt} [{rate_fmt}{postfix}]',
			'postfix':'',
			'total':total,
			'file':output,
			'position':position,
			'leave':True,
			'dynamic_ncols':dynamic_ncols,
		}
		self.bar = tqdm(**bar_kwargs)
		self.done_ = False

	def __call__(self,
		txt:str='???',
		update:bool=True,
		):
		assert isinstance(txt, str)
		self.bar.set_postfix_str(txt)
		#d.set_description(d)
		if update:
			self.bar.update(1)
			
	def done(self):
		if not self.done_:
			self.bar.close()