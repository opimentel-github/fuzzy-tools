from __future__ import print_function
from __future__ import division
from . import _C

import numpy as np
from scipy import stats
from ..strings import xstr
from .xerror import XError
from ..dataframes import DFBuilder
import math
from mlxtend.evaluate import permutation_test
from ..progress_bars import ProgressBar

DEFAULT_TH_PVALUE = .05
NUM_ROUNDS = 1e4
RANDOM_STATE = 0
ALTERNATIVE = 'two-sided' # two-sided less greater
TH_PVALUE_TXT = DEFAULT_TH_PVALUE
SHAPIRO_TH_PVALUE = DEFAULT_TH_PVALUE
N_DECIMALS = _C.N_DECIMALS
PVALUE_CHAR = '$p$'
NULL_CHAR = ''
PVALUE_SYMBOLS = {
	'***':[-np.inf, .001],
	'**':[.001, .01],
	'*':[.01, .05],
	'+':[.05, .1],
	'':[.1, np.inf],
	}
CHECK_SAMPLES = True

###################################################################################################################################################

def _check_xe(xe):
	assert len(xe)>=1 and len(xe.shape)==1

def get_pvalue_symbol(pvalue,
	get_upper_bound=False,
	):
	if pvalue is None:
		return 'x'
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

def format_pvalue(pvalue, mean_diff,
	th_pvalue_txt=TH_PVALUE_TXT,
	n_decimals=N_DECIMALS,
	):
	if pvalue is None:
		return NULL_CHAR
	mean_diff_txt = xstr(mean_diff,
		n_decimals=n_decimals,
		)
	txt = f'$\Delta$={mean_diff_txt}{get_pvalue_symbol(pvalue)}'
	if pvalue>th_pvalue_txt:
		txt = f'{txt}; {PVALUE_CHAR}={xstr(pvalue)}'
	return txt

def _normalitytest(x,
	shapiro_th_pvalue=SHAPIRO_TH_PVALUE,
	):
	pvalue = stats.shapiro(x).pvalue
	is_normal = not pvalue<shapiro_th_pvalue
	return is_normal

def _permutation_test(x1, x2,
	alternative=ALTERNATIVE,
	num_rounds=NUM_ROUNDS,
	random_state=RANDOM_STATE,
	):
	pvalue = permutation_test(x1, x2,
		method='approximate',
		num_rounds=int(num_rounds),
		seed=random_state,
		)
	if alternative=='two-sided':
		pvalue = pvalue
	elif alternative=='greater':
		pvalue = pvalue/2
	else:
		raise Exception(f'{alternative}')
	return pvalue

###################################################################################################################################################

def ttest(x1, x2,
	alternative=ALTERNATIVE,
	shapiro_th_pvalue=SHAPIRO_TH_PVALUE,
	):
	pvalue = None
	if type(x1)==XError and type(x2)==XError:
		_check_xe(x1)
		_check_xe(x2)
		pass

	else:
		raise Exception(f'{type(x1)}; {type(x2)}')

	return pvalue

def welchtest(x1, x2,
	alternative=ALTERNATIVE,
	shapiro_th_pvalue=SHAPIRO_TH_PVALUE,
	):
	pvalue = None
	if type(x1)==XError and type(x2)==XError:
		_check_xe(x1)
		_check_xe(x2)
		normal_kwargs = {
			'shapiro_th_pvalue':shapiro_th_pvalue,
			}
		x1 = x1._x
		x2 = x2._x
		both_are_normal = _normalitytest(x1, **normal_kwargs) and _normalitytest(x2, **normal_kwargs)
		if both_are_normal:
			tvalue, pvalue = stats.ttest_ind(x1, x2,
				alternative=alternative,
				equal_var=False, # welch
				)

	else:
		raise Exception(f'{type(x1)}; {type(x2)}')

	return pvalue

def permutationtest(x1, x2,
	alternative=ALTERNATIVE,
	num_rounds=NUM_ROUNDS,
	random_state=RANDOM_STATE,
	):
	pvalue = None
	if type(x1)==XError and type(x2)==XError:
		_check_xe(x1)
		_check_xe(x2)
		x1 = x1._x
		x2 = x2._x
		pvalue = _permutation_test(x1, x2,
			alternative=alternative,
			num_rounds=num_rounds,
			random_state=random_state,
			)

	else:
		raise Exception(f'{type(x1)}; {type(x2)}')

	return pvalue

###################################################################################################################################################

def gridtest_greater(values_dict, test,
	check_samples=CHECK_SAMPLES,
	th_pvalue_txt=TH_PVALUE_TXT,
	n_decimals=N_DECIMALS,
	test_kwargs={}
	):
	pvalue_symbols = get_pvalue_symbols()
	for pvalue_symbol in pvalue_symbols.keys():
		print(f'{pvalue_symbols[pvalue_symbol]} pvalue{pvalue_symbol}')
	df_builder = DFBuilder()
	n = 10
	keys = list(values_dict.keys())
	bar = ProgressBar(len(keys)**2)
	for key1 in keys:
		d = {}
		x1 = values_dict[key1]
		for key2 in keys:
			bar(f'{key1} v/s {key2}')
			x2 = values_dict[key2]
			pvalue, mean_diff = greatertest(x1, x2, test,
				check_samples=check_samples,
				test_kwargs=test_kwargs,
				)
			pvalue_txt = format_pvalue(pvalue, mean_diff,
				th_pvalue_txt=th_pvalue_txt,
				n_decimals=n_decimals,
				)
			d[f'{key2}; #samples={len(x2)}'] = f'{pvalue_txt}'
		df_builder.append(f'{key1}; #samples={len(x1)}', d)
	bar.done()
	return df_builder.get_df()

def greatertest(x1, x2, test,
	check_samples=CHECK_SAMPLES,
	test_kwargs={},
	):
	'''
	check if mean(x1)>mean(x2) with statistical significance
	'''
	if check_samples:
		assert len(x1)==len(x2)
	mean_diff = x1.get_mean()-x2.get_mean()
	if mean_diff<=0:
		return None, None
	pvalue = test(x1, x2,
		alternative='greater',
		**test_kwargs,
		)
	return pvalue, mean_diff