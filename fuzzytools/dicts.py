from __future__ import print_function
from __future__ import division
from __future__ import annotations
from . import _C

from nested_dict import nested_dict
import copy

###################################################################################################################################################

def update_dicts(d_list):
	assert isinstance(d_list, list)
	d = {}
	for _d in d_list:
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