from __future__ import print_function
from __future__ import division
from . import _C

import numpy as np
from scipy import stats
from ..strings import xstr
from .xerror import XError
from ..dataframes import DFBuilder

TH_PVALUE = 0.05
LOWER_BOUND = 0.001
UPPER_BOUND = 0.99

###################################################################################################################################################

def _check_values(values):
	assert isinstance(values, list) or isinstance(values, np.ndarray)
	return values

def grid_is_greater_test(values_dict, test):
	df_builder = DFBuilder()
	for key1 in values_dict.keys():
		d = {}
		values1 = _check_values(values_dict[key1])
		for key2 in values_dict.keys():
			values2 = _check_values(values_dict[key2])
			is_significant_greater, pvalue = test(values1, values2)
			d[key2] = pvalue

		df_builder.append(key1, d)

	return df_builder.get_df()

###################################################################################################################################################

def format_pvalue(pvalue,
	lower_bound=LOWER_BOUND,
	upper_bound=UPPER_BOUND,
	):
	txt = f'p={xstr(pvalue)}'
	if pvalue<lower_bound:
		txt = f'p<{xstr(lower_bound)}'
	if pvalue>upper_bound:
		txt = f'p>{xstr(upper_bound)}'
	return txt

def welch_is_greater_test(_x1, _x2,
	th_pvalue=TH_PVALUE,
	lower_bound=LOWER_BOUND,
	upper_bound=UPPER_BOUND,
	verbose=0,
	):
	if np.mean(_x1)>np.mean(_x2):
		x1 = _x1
		x2 = _x2
	else:
		x1 = _x2
		x2 = _x1
	return _welch_is_greater_test(x1, x2,
		th_pvalue=th_pvalue,
		lower_bound=lower_bound,
		upper_bound=upper_bound,
		verbose=verbose,
		)

def _welch_is_greater_test(_x1, _x2,
	th_pvalue=TH_PVALUE,
	lower_bound=LOWER_BOUND,
	upper_bound=UPPER_BOUND,
	verbose=0,
	):
	'''
	check x1>x2 with statistical significance
	'''
	x1 = np.array(_x1)
	x2 = np.array(_x2)
	assert len(x1)>=1 and len(x1.shape)==1
	assert len(x2)>=1 and len(x2.shape)==1
	statistic, pvalue = stats.ttest_ind(x1, x2,
		alternative='greater', # two-sided less greater
		equal_var=False, # welch
		)
	x1_xe = XError(x1)
	x2_xe = XError(x2)
	assert x1_xe.mean>=x2_xe.mean
	is_significant_greater = pvalue<th_pvalue
	if verbose:
		print(f'th-p-value={th_pvalue}')
		print(f'x1={x1_xe}')
		print(f'x2={x2_xe}')
		if is_significant_greater:
			print(f'x1>x2 with {format_pvalue(pvalue, lower_bound, upper_bound)}')
		else:
			print(f'!x1>x2 with {format_pvalue(pvalue, lower_bound, upper_bound)}')
	return is_significant_greater, pvalue