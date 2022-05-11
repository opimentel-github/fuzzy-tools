from __future__ import print_function
from __future__ import division
from . import _C

import numpy as np
from ..strings import xstr
from ..dataframes import DFBuilder

N = None

###################################################################################################################################################

class TopRank():
	def __init__(self,
		name='',
		n=N,
		uses_info=True,
		):
		self.name = name
		self.n = n
		self.uses_info = uses_info
		self.reset()

	def reset(self):
		self.need_calcule = True
		self.names = []
		self.values = []
		self.infos = []
		self.idxs = None
		
	def add_list(self, names, values,
		infos=None,
		):
		infos = [None for _ in values] if infos is None else infos
		for k in range(len(values)):
			self.append(names[k], values[k], infos[k])

	def append(self, name, value,
		info=None,
		):
		self.names.append(name)
		self.values.append(value)
		self.infos.append(info)
		self.need_calcule = True
		
	def calcule(self):
		if self.need_calcule:
			self.idxs = np.argsort(self.values)[::-1].tolist() # high values first
			self.need_calcule = False
		
	def __call__(self):
		self.calcule()
		return self

	def __getitem__(self, idx):
		k = self.idxs[idx]
		return self.names[k], self.values[k], self.infos[k]

	def __len__(self):
		return self.n if len(self.values) is None else self.n

	def __repr__(self):
		self.calcule() # just in case
		txt = f'{self.name}:\n'
		for k in range(0, len(self)):
			idx = self.idxs[k]
			txt += f'[{k+1}#] {self.names[idx]}={xstr(self.values[idx], n_decimals=4)}\n'
		return txt[:-1]

	def get_df(self,
		include_position=True,
		):
		self.calcule() # just in case
		info_df = DFBuilder()
		for k in range(0, len(self)):
			idx = self.idxs[k]
			d = {}
			if include_position:
				d.update({'_k':k+1})
			d[self.name] = self.values[idx]
			info_df.append(self.names[idx], d)
		return info_df.get_df()