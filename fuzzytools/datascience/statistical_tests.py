from __future__ import print_function
from __future__ import division
from . import _C

import numpy as np
from scipy import stats
from ..strings import xstr
from .xerror import XError, Measurement
from ..dataframes import DFBuilder
import math

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

def format_pvalue(tvalue, pvalue, mean_diff,
	include_pvalue_txt=INCLUDE_PVALUE_TXT,
	n_decimals=N_DECIMALS,
	):
	if tvalue is None:
		return NULL_CHAR
	mean_diff_txt = xstr(mean_diff,
		n_decimals=n_decimals,
		)
	txt = f'$\Delta$={mean_diff_txt}{get_pvalue_symbol(pvalue)}'
	if include_pvalue_txt:
		txt = f'{txt}; {PVALUE_CHAR}={xstr(pvalue)}'
	return txt

###################################################################################################################################################

def normaltest(x,
	shapiro_th_pvalue=SHAPIRO_TH_PVALUE,
	):
	pvalue = stats.shapiro(x).pvalue
	is_normal = not pvalue<shapiro_th_pvalue
	return is_normal

def ttest(x1, x2,
	alternative=ALTERNATIVE,
	shapiro_th_pvalue=SHAPIRO_TH_PVALUE,
	):
	tvalue = None
	pvalue = None
	if isinstance(x1, XError) and isinstance(x2, XError):
		assert len(x1)>=1 and len(x1.shape)==1
		assert len(x2)>=1 and len(x2.shape)==1
		pass

	elif isinstance(x1, Measurement) and isinstance(x2, Measurement):
		s = math.sqrt(((len(x1)-1)*x1.get_std()**2+(len(x2)-1)*x2.get_std()**2)/(len(x1)+len(x2)-2))
		se = s*math.sqrt(1/len(x1)+1/len(x2))
		tvalue = (x1.get_mean()-x2.get_mean())/se
		df = len(x1)+len(x2)-2
		if alternative=='two-sided':
			pvalue = stats.t.sf(abs(tvalue), df)*2
		if alternative=='greater':
			pvalue = stats.t.sf(abs(tvalue), df)
	else:
		raise Exception(f'')

	return tvalue, pvalue

def welchtest(x1, x2,
	alternative=ALTERNATIVE,
	shapiro_th_pvalue=SHAPIRO_TH_PVALUE,
	):
	tvalue = None
	pvalue = None
	if isinstance(x1, XError) and isinstance(x2, XError):
		assert len(x1)>=1 and len(x1.shape)==1
		assert len(x2)>=1 and len(x2.shape)==1
		normal_kwargs = {
			'shapiro_th_pvalue':shapiro_th_pvalue,
			}
		x1 = x1._x
		x2 = x2._x
		both_are_normal = normaltest(x1, **normal_kwargs) and normaltest(x2, **normal_kwargs)
		if both_are_normal:
			tvalue, pvalue = stats.ttest_ind(x1, x2,
				alternative=alternative,
				equal_var=False, # welch
				)

	elif isinstance(x1, Measurement) and isinstance(x2, Measurement):
		s = math.sqrt(((len(x1)-1)*x1.get_std()**2+(len(x2)-1)*x2.get_std()**2)/(len(x1)+len(x2)-2))
		se = s*math.sqrt(1/len(x1)+1/len(x2))
		tvalue = (x1.get_mean()-x2.get_mean())/se
		df = len(x1)+len(x2)-2
		if alternative=='two-sided':
			pvalue = scipy.stats.t.sf(abs(tvalue), df)*2
		if alternative=='greater':
			pvalue = scipy.stats.t.sf(abs(tvalue), df)
	else:
		raise Exception(f'')

	return tvalue, pvalue

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
			tvalue, pvalue, mean_diff = greatertest(x1, x2, test,
				shapiro_th_pvalue=shapiro_th_pvalue,
				)
			pvalue_txt = format_pvalue(tvalue, pvalue, mean_diff,
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
		return None, None, None
	tvalue, pvalue = test(x1, x2,
		alternative='greater',
		shapiro_th_pvalue=shapiro_th_pvalue,
		)
	return tvalue, pvalue, mean_diff