from __future__ import print_function
from __future__ import division
from . import _C

import numpy as np

###################################################################################################################################################

def softmax(_x,
	axis=0,
	):
	x = np.exp(np.array(_x))
	x /= np.sum(x, axis=axis)
	return x