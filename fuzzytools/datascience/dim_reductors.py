from __future__ import print_function
from __future__ import division
from __future__ import annotations
from . import _C

# from sklearn.preprocessing import QuantileTransformer, StandardScaler
# from sklearn.decomposition import PCA, KernelPCA, FastICA
# from sklearn.manifold import TSNE
# from umap import UMAP
from sklearn.decomposition import PCA
import numpy as np
from copy import copy, deepcopy

###################################################################################################################################################

def _check(x):
	assert len(x.shape)==2

###################################################################################################################################################

class DimReductorPipeline():
	def __init__(self, pipeline):
		self.pipeline = pipeline
		self.reset()

	def reset(self):
		self.fitted = False

	def __len__(self):
		return len(self.pipeline)

	def get_fit_preprocessed_data(self, x,
		drop_duplicates=False,
		normal_std=0,
		):
		new_x = np.concatenate(x, axis=0) if type(x)==list else copy(x)
		_check(new_x)
		if drop_duplicates:
			print('deleting duplicates', new_x.shape)
			new_x = np.unique(new_x, axis=0) # drop duplicated
			print(new_x.shape)
		if normal_std>0:
			new_x = new_x+np.random.normal(0, normal_std, size=new_x.shape)
		return new_x

	def fit(self, x,
		drop_duplicates=False,
		normal_std=0,
		reduction_map_kwargs={},
		):
		new_x = self.get_fit_preprocessed_data(x,
			drop_duplicates=drop_duplicates,
			normal_std=normal_std,
			)
		for k,method in enumerate(self.pipeline):
			new_x = method.fit_transform(new_x) if k<len(self)-1 else method.fit(new_x)
		self.fitted = True

	def transform(self, x,
		reduction_map_kwargs={},
		verbose=0,
		):
		assert self.fitted
		new_x = copy(x)
		_check(new_x)
		for method in self.pipeline:
			old_shape = new_x.shape
			new_x = method.transform(new_x)
			if verbose:
				print(f'{old_shape}>{new_x.shape}')
		return new_x