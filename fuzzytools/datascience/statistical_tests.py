from __future__ import print_function
from __future__ import division
from . import _C

import numpy as np
from scipy import stats
from ..strings import xstr
from .xerror import XError
from ..dataframes import DFBuilder

NORMAL_TH_PVALUE = .05
N_DECIMALS = _C.N_DECIMALS
PVALUE_CHAR = '$p_v$'
NULL_CHAR = ''
PVALUE_SYMBOLS = {
	'***':[-np.inf, .001],
	'**':[.001, .01],
	'*':[.01, .05],
	'+':[.05, .01],
	'':[.01, np.inf],
	}

###################################################################################################################################################

def _check_values(values):
	assert isinstance(values, list) or isinstance(values, np.ndarray)
	return values

def get_pvalue_symbol(pvalue,
	get_upper_bound=False,
	):
	symbols = list(PVALUE_SYMBOLS.keys())
	for s in symbols:
		lower_bound = PVALUE_SYMBOLS[s][0]
		upper_bound = PVALUE_SYMBOLS[s][-1]
		if pvalue>lower_bound and pvalue<=upper_bound:
			if get_upper_bound:
				return upper_bound, s
			else:
				return s

def get_pvalue_symbols():
	symbols = list(PVALUE_SYMBOLS.keys())
	return {f'<={PVALUE_SYMBOLS[s][-1]}':s for s in symbols}

def is_normal(x,
	th_pvalue=NORMAL_TH_PVALUE,
	):
	pvalue = stats.shapiro(x).pvalue
	return not pvalue<th_pvalue

def grid_is_greater_test(values_dict, test,
	n_decimals=N_DECIMALS,
	):
	print(get_pvalue_symbols())
	df_builder = DFBuilder()
	for key1 in values_dict.keys():
		d = {}
		values1 = _check_values(values_dict[key1])
		for key2 in values_dict.keys():
			values2 = _check_values(values_dict[key2])
			if np.mean(values1)<np.mean(values2):
				d[key2] = NULL_CHAR
			else:
				diff, pvalue, pvalue_txt = test(values1, values2,
					n_decimals=n_decimals,
					)
				d[key2] = f'{pvalue_txt}'

		df_builder.append(key1, d)

	return df_builder.get_df()

###################################################################################################################################################

def format_pvalue(pvalue, diff):
	if pvalue is None:
		return NULL_CHAR
	txt = f'$\Delta$={xstr(diff)}{get_pvalue_symbol(pvalue)}; {PVALUE_CHAR}={xstr(pvalue)}'
	return txt

def welch_is_greater_test(_x1, _x2,
	verbose=0,
	sort=False,
	n_decimals=N_DECIMALS,
	):
	'''
	check if mean(x1)>mean(x2) with statistical significance
	'''
	assert len(_x1)>=1 and len(_x1.shape)==1
	assert len(_x2)>=1 and len(_x2.shape)==1
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
	pvalue = None
	are_normal = is_normal(x1) and is_normal(x2)
	if verbose:
		print(f'are_normal={are_normal}')
	if are_normal:
		statistic, pvalue = stats.ttest_ind(x1, x2,
			alternative='greater', # two-sided less greater
			equal_var=False, # welch
			)

	pvalue_txt = format_pvalue(pvalue, diff)
	return diff, pvalue, pvalue_txt