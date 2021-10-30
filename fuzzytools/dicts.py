from __future__ import print_function
from __future__ import division
from __future__ import annotations
from . import _C

from . import lists
from nested_dict import nested_dict
import copy

###################################################################################################################################################

def get_random_key(d:dict):
	keys = list(d.keys())
	key = lists.get_random_item(keys)
	return key

def update_dicts(dicts):
	d = {}
	for _d in dicts:
		assert isinstance(_d, dict)
		d.update(_d)
	return d

def along_dict_obj_method(obj_dict, obj_method,
	obj_args=[],
	obj_kwargs={},
	):
	_obj_dict = nested_dict(obj_dict)
	for keys_as_tuple,value in _obj_dict.items_flat():
		getattr(value, obj_method)(*obj_args, **obj_kwargs)
	return _obj_dict.to_dict()