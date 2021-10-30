from __future__ import print_function
from __future__ import division
from . import _C

from ..strings import get_bar
import itertools

###################################################################################################################################################

def search_Iter(d:dict, aux_d:dict):
	if type(d)==dict:
		keys = list(d.keys())
		for key in keys:
			search_Iter(d[key], aux_d)

	elif type(d)==GDIter:
		indexs = list(range(len(d.args)))
		aux_d[id(d)] = indexs
	else:
		pass

def create_new_dict(d:dict, id_indexs:list):
	if type(d)==dict:
		keys = list(d.keys())
		new_dict = {}
		for key in keys:
			value = create_new_dict(d[key], id_indexs)
			new_dict[key] = value
		return new_dict

	elif type(d)==GDIter:
		index = id_indexs[id(d)]
		return d.args[index]

	else:
		return d

def decompose_dict_Iter(d:dict):
	assert type(d)==dict
	
	# search for GDIter objects
	handler_dict = {}
	keys = list(d.keys())
	aux_dict = {}
	search_Iter(d, aux_dict)
	aux_dict_keys = list(aux_dict.keys())
	if len(aux_dict_keys)==0:
		return [d]

	iter_args = [aux_dict[k] for k in aux_dict_keys]
	prod = list(itertools.product(*iter_args))
	id_indexs_list = []
	for p in prod:
		id_indexs_list.append({k:p[n] for n,k in enumerate(aux_dict_keys)})
	#print(id_indexs)

	sub_dicts = []
	for id_indexs in id_indexs_list:
		#print(' >>>  id_indexs',id_indexs)
		new_dict = create_new_dict(d, id_indexs)
		#print(new_dict)
		sub_dicts.append(new_dict)

	return sub_dicts

###################################################################################################################################################

class GDIter():
	def __init__(self, *args):
		super().__init__()
		self.args = args

class GridSeacher():
	def __init__(self, parameters_dict):
		super().__init__()
		self.params_grid = decompose_dict_Iter(parameters_dict.copy())

	def __len__(self):
		return len(self.params_grid)

	def __getitem__(self, idx):
		return self.params_grid[idx]

	def update(self, d):
		for k in d.keys():
			for pg in self.params_grid:
				pg[k] = d[k]
				pass

	def get_dicts(self):
		return self.params_grid

	def __repr__(self):
		txt = ''
		for k in range(len(self)):
			txt += f'({k}) - {self[k]}\n'
			txt += get_bar()+'\n'
		return txt

	def __add__(self, other):
		if self is None or self==0:
			return other

		elif other is None or other==0:
			return self

		elif type(self)==GridSeacher and type(other)==GridSeacher:
			gs = GridSeacher({})
			gs.params_grid = self.params_grid+other.params_grid
			return gs

		else:
			raise Exception(f'{type(self)}; {type(other)}')

	def __radd__(self, other):
		return self+other