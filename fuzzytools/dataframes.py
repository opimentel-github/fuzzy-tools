from __future__ import print_function
from __future__ import division
from . import _C

import pandas as pd
#from nested_dict import nested_dict
import numpy as np

###################################################################################################################################################

def clean_df_nans(df,
	mode='value', # value mean median
	nan_value=_C.NAN_VALUE,
	df_values=None,
	):
	new_df = df.replace([np.inf, -np.inf], np.nan) # replace infinites to nan
	null_cols = list(new_df.columns[new_df.isnull().all()])
	new_df = new_df.drop(null_cols, axis='columns')
	if mode=='value':
		new_df = new_df.fillna(nan_value)

	elif mode=='mean':
		df_values = new_df.mean(axis='index', skipna=True) if df_values is None else df_values
		new_df = new_df.fillna(df_values)

	elif mode=='median':
		df_values = new_df.median(axis='index', skipna=True) if df_values is None else df_values
		new_df = new_df.fillna(df_values)

	return new_df, df_values, null_cols

###################################################################################################################################################

class DFBuilder():
	def __init__(self):
		self.reset()

	def reset(self):
		self.counter = 0
		self.indexs = []
		self.ds = []

	def append(self, index, d):
		assert isinstance(d, dict)
		index = self.counter if index is None else index
		self.indexs += [index]
		self.ds += [d]
		self.counter += 1
	
	def __getitem__(self, idx):
		k = self.indexs.index(idx)
		return self.ds[k]

	def __len__(self):
		return len(self.indexs)

	def __repr__(self):
		df = self.get_df()
		return str(df)

	def get_df(self):
		assert len(self)==len(list(set(self.indexs))), 'indexs must be unique'
		new_d = {index:{} for index in self.indexs}
		for index,d in zip(self.indexs,self.ds):
			for k in d.keys():
				new_d[index][k] = d[k]
		df = pd.DataFrame.from_dict(new_d, orient='index').reindex(self.indexs)
		return df

	def __call__(self):
		return self.get_df()