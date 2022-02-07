from __future__ import print_function
from __future__ import division
from . import _C

import pandas as pd
import numpy as np

###################################################################################################################################################

def get_bar_latex(new_model_attrs, results_columns,
	uses_separator=False,
	):
	assert len(new_model_attrs)>0
	assert len(results_columns)>0
	separator = '|' if uses_separator else ''
	txt = 'c'*len(new_model_attrs)+separator+'c'*len(results_columns)
	txt = 'l'+txt[1:]
	return txt

def dict_to_dataframe(info_dict):
	return pd.DataFrame.from_dict(info_dict, orient='index'),

def get_cmidrule(c1, c2,
	tickness=None,
	):
	if tickness is None:
		txt = '\\cmidrule{'+str(c1)+'-'+str(c2)+'}'
	else:
		txt = '\\Xcline{'+str(c1)+'-'+str(c2)+'}{'+str(tickness)+'pt}'
	return txt

def get_bold(s:str):
	return '\\textbf{'+s+'}'