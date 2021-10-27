from __future__ import print_function
from __future__ import division
from . import _C

import numpy as np
from scipy import stats
from ..strings import xstr
from .xerror import XError, Measurement
from ..dataframes import DFBuilder
import math
from mlxtend.evaluate import permutation_test

NUM_ROUNDS = 1e5
RANDOM_STATE = 0
ALTERNATIVE = 'two-sided' # two-sided less greater
DEFAULT_TH_PVALUE = .05
INCLUDE_PVALUE_TXT = False
SHAPIRO_TH_PVALUE = DEFAULT_TH_PVALUE
N_DECIMALS = _C.N_DECIMALS
PVALUE_CHAR = '$p_v$'
NULL_CHAR = ''
PVALUE_SYMBOLS = {
	'***':[-np.inf, .001],
	'**':[.001, .01],
	'*':[.01, .05],
	'+':[.05, .1],
	'':[.1, np.inf],
	}

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
	include_pvalue_txt=INCLUDE_PVALUE_TXT,
	n_decimals=N_DECIMALS,
	):
	if pvalue is None:
		return NULL_CHAR
	mean_diff_txt = xstr(mean_diff,
		n_decimals=n_decimals,
		)
	txt = f'$\Delta$={mean_diff_txt}{get_pvalue_symbol(pvalue)}'
	if include_pvalue_txt:
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
	):
	pvalue = permutation_test(x1, x2,
		method='approximate',
		num_rounds=NUM_ROUNDS,
		seed=int(RANDOM_STATE),
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

	elif type(x1)==Measurement and type(x2)==Measurement:
		s = math.sqrt(((len(x1)-1)*x1.get_std()**2+(len(x2)-1)*x2.get_std()**2)/(len(x1)+len(x2)-2))
		se = s*math.sqrt(1/len(x1)+1/len(x2))
		tvalue = (x1.get_mean()-x2.get_mean())/se
		df = len(x1)+len(x2)-2
		pvalue = stats.t.sf(abs(tvalue), df)
		if alternative=='two-sided':
			pvalue = pvalue*2
		elif alternative=='greater':
			pvalue = pvalue
		else:
			raise Exception(f'{alternative}')
	else:
		raise Exception(f'{type(x1)} {type(x2)}')

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

	elif type(x1)==Measurement and type(x2)==Measurement:
		pass

	else:
		raise Exception(f'{type(x1)} {type(x2)}')

	return pvalue

def permutationtest(x1, x2,
	alternative=ALTERNATIVE,
	shapiro_th_pvalue=SHAPIRO_TH_PVALUE,
	):
	pvalue = None
	if type(x1)==XError and type(x2)==XError:
		_check_xe(x1)
		_check_xe(x2)
		x1 = x1._x
		x2 = x2._x
		pvalue = _permutation_test(x1, x2,
			alternative=alternative,
			)

	elif type(x1)==Measurement and type(x2)==Measurement:
		pass

	else:
		raise Exception(f'{type(x1)} {type(x2)}')

	return pvalue

###################################################################################################################################################

def gridtest_greater(values_dict, test,
	shapiro_th_pvalue=SHAPIRO_TH_PVALUE,
	include_pvalue_txt=INCLUDE_PVALUE_TXT,
	n_decimals=N_DECIMALS,
	):
	print(get_pvalue_symbols())
	df_builder = DFBuilder()
	for key1 in values_dict.keys():
		d = {}
		x1 = values_dict[key1]
		for key2 in values_dict.keys():
			x2 = values_dict[key2]
			pvalue, mean_diff = greatertest(x1, x2, test,
				shapiro_th_pvalue=shapiro_th_pvalue,
				)
			pvalue_txt = format_pvalue(pvalue, mean_diff,
				include_pvalue_txt=include_pvalue_txt,
				n_decimals=n_decimals,
				)
			d[key2] = f'{pvalue_txt}'
		df_builder.append(key1, d)
	return df_builder.get_df()

def greatertest(x1, x2, test,
	shapiro_th_pvalue=SHAPIRO_TH_PVALUE,
	):
	'''
	check if mean(x1)>mean(x2) with statistical significance
	'''
	mean_diff = x1.get_mean()-x2.get_mean()
	if mean_diff<0:
		return None, None
	pvalue = test(x1, x2,
		alternative='greater',
		shapiro_th_pvalue=shapiro_th_pvalue,
		)
	return pvalue, mean_diff