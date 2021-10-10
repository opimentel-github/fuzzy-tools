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
PVALUE_CHAR = '$p^*$'
N_DECIMALS = _C.N_DECIMALS

###################################################################################################################################################

def _check_values(values):
	assert isinstance(values, list) or isinstance(values, np.ndarray)
	return values

def grid_is_greater_test(values_dict, test,
	n_decimals=N_DECIMALS,
	):
	df_builder = DFBuilder()
	for key1 in values_dict.keys():
		d = {}
		values1 = _check_values(values_dict[key1])
		for key2 in values_dict.keys():
			values2 = _check_values(values_dict[key2])
			if np.mean(values1)<np.mean(values2):
				d[key2] = '-'
			else:
				is_significant_greater, pvalue, pvalue_txt, diff = test(values1, values2,
					n_decimals=n_decimals,
					)
				d[key2] = f'{pvalue_txt} ($\\Delta$={xstr(diff)})'

		df_builder.append(key1, d)

	return df_builder.get_df()

###################################################################################################################################################

def format_pvalue(pvalue,
	th_pvalue=TH_PVALUE,
	lower_bound=LOWER_BOUND,
	upper_bound=UPPER_BOUND,
	):
	if pvalue<lower_bound:
		txt = f'{PVALUE_CHAR}<{xstr(lower_bound)}'
	elif pvalue>upper_bound:
		txt = f'{PVALUE_CHAR}>{xstr(upper_bound)}'
	else:
		txt = f'{PVALUE_CHAR}={xstr(pvalue)}'
	if pvalue<th_pvalue:
		txt = f'{txt}<{xstr(th_pvalue)}'
	return txt

def welch_is_greater_test(_x1, _x2,
	th_pvalue=TH_PVALUE,
	lower_bound=LOWER_BOUND,
	upper_bound=UPPER_BOUND,
	verbose=0,
	sort=False,
	n_decimals=N_DECIMALS,
	):
	'''
	check x1>x2 with statistical significance
	'''
	if sort:
		if np.mean(_x1)>np.mean(_x2):
			x1 = np.array(_x1)
			x2 = np.array(_x2)
		else:
			x1 = np.array(_x2)
			x2 = np.array(_x1)
	else:
		x1 = np.array(_x1)
		x2 = np.array(_x2)
	assert len(x1)>=1 and len(x1.shape)==1
	assert len(x2)>=1 and len(x2.shape)==1
	statistic, pvalue = stats.ttest_ind(x1, x2,
		alternative='greater', # two-sided less greater
		equal_var=False, # welch
		)
	
	is_significant_greater = pvalue<th_pvalue
	pvalue_txt = format_pvalue(pvalue, th_pvalue, lower_bound, upper_bound)
	mean_x1 = xstr(np.mean(x1),
		n_decimals=n_decimals,
		remove_zero=False,
		)
	mean_x2 = xstr(np.mean(x2),
		n_decimals=n_decimals,
		remove_zero=False,
		)
	diff = float(mean_x1)-float(mean_x2)
	assert diff>=0
	if verbose:
		print(f'th-p-value={th_pvalue}')
		print(f'x1={XError(x1)}')
		print(f'x2={XError(x2)}')
		if is_significant_greater:
			print(f'x1>x2 with {pvalue_txt}')
		else:
			print(f'!x1>x2 with {pvalue_txt}')
	return is_significant_greater, pvalue, pvalue_txt, diff