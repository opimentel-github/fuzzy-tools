from __future__ import print_function
from __future__ import division
from . import _C

import sys, os
from . import strings

###################################################################################################################################################

class HiddenPrints():
	def __enter__(self):
		self._original_stdout = sys.stdout
		sys.stdout = open(os.devnull, 'w')

	def __exit__(self, exc_type, exc_val, exc_tb):
		sys.stdout.close()
		sys.stdout = self._original_stdout

class ShowPrints():
	def __enter__(self):
		pass

	def __exit__(self, exc_type, exc_val, exc_tb):
		pass

###################################################################################################################################################

def print_bar(
	char=_C.MIDDLE_LINE_CHAR,
	N=_C.BAR_SIZE,
	):
	print(strings.get_bar(char, N))

def print_big_bar():
	print_bar(_C.TOP_SQUARE_CHAR)

def full_print(x,
	flush=False,
	end='\n',
	):
	print(x, flush=flush, end=end)

def null_print(x,
	flush=False,
	end='\n',
	):
	pass

def print_red(txt,
	print_f=full_print,
	):
	if not txt is None:
		print_f(strings.color_str(txt, 'red'))

def print_yellow(txt,
	print_f=full_print,
	):
	if not txt is None:
		print_f(strings.color_str(txt, 'yellow'))

def print_blue(txt,
	print_f=full_print,
	):
	if not txt is None:
		print_f(strings.color_str(txt, 'blue'))

def print_green(txt,
	print_f=full_print,
	):
	if not txt is None:
		print_f(strings.color_str(txt, 'green'))