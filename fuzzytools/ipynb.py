from __future__ import print_function
from __future__ import division
from . import _C

import sys

###################################################################################################################################################

def type_of_script():
	try:
		ipy_str = str(type(get_ipython()))
		if 'zmqshell' in ipy_str:
			return 'jupyter'
		if 'terminal' in ipy_str:
			return 'ipython'
	except:
		return 'terminal'

def in_ipynb():
	return not type_of_script()=='terminal'