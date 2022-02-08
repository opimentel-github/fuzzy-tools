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

class DimReductor():
	def __init__(self, scaler, reduction_map,
		inter_pca_dims=None,
		):
		self.scaler = scaler
		self.reduction_map = reduction_map
		self.inter_pca_dims = inter_pca_dims
		self.reset()

	def reset(self):
		self.fitted = False
		self.n_components = self.reduction_map.n_components

	def fit(self, x,
		drop_duplicates=False,
		normal_std=0,
		reduction_map_kwargs={},
		):
		new_x = np.concatenate(x, axis=0) if type(x)==list else copy(x)
		_check(new_x)
			
		if drop_duplicates:
			print('deleting duplicates', new_x.shape)
			new_x = np.unique(new_x, axis=0) # drop duplicated
			print(new_x.shape)

		new_x = new_x+np.random.normal(0, normal_std, size=new_x.shape) if normal_std>0 else new_x
		new_x = self.scaler.fit_transform(new_x)
		if not self.inter_pca_dims is None:
			if not hasattr(self, 'pca'):
				self.pca = PCA(n_components=self.inter_pca_dims )
			new_x = self.pca.fit_transform(new_x)
		_ = self.reduction_map.fit(new_x, **reduction_map_kwargs)
		self.fitted = True

	def transform(self, x,
		reduction_map_kwargs={},
		):
		assert self.fitted
		new_x = copy(x)
		_check(new_x)
		
		new_x = self.scaler.transform(new_x)
		if not self.inter_pca_dims is None:
			new_x = self.pca.transform(new_x)
		new_x = self.reduction_map.transform(new_x, **reduction_map_kwargs)
		return new_x

	def fit_transform(self, x,
		reduction_map_kwargs={},
		):
		self.fit(x,
			reduction_map_kwargs=reduction_map_kwargs,
			)
		new_x = self.transform(x,
			reduction_map_kwargs=reduction_map_kwargs,
			)
		return new_x