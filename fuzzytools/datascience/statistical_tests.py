from __future__ import print_function
from __future__ import division
from . import _C

import numpy as np
from scipy import stats

TH_PVALUE = 0.05

###################################################################################################################################################

def welch_test_is_greater(_a, _b,
	th_pvalue=TH_PVALUE,
	verbose=1,
	alternative='two-sided',
	):
	a = np.array(_a)
	b = np.array(_b)
	assert len(a)>=1 and len(a.shape)==1
	assert len(b)>=1 and len(b.shape)==1
	tvalue, pvalue = stats.ttest_ind(a, b,
		equal_var=False,	
		alternative=alternative,
		)
	a_mean = np.mean(a)
	b_mean = np.mean(b)
	is_greater = a_mean>b_mean
	is_significant_greater = is_greater and pvalue<th_pvalue
	if verbose:
		if is_significant_greater:
			print(f'a>b ({a_mean}>{b_mean}) with p-value={pvalue}<{th_pvalue}')
		else:
			print(f'not a>b (not {a_mean}>{b_mean}) with p-value={pvalue}>{th_pvalue}')
	return is_greater, is_significant_greater, pvalue