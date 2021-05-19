#!/usr/bin/env python3
import sys
sys.path.append('../') # or just install the module

if __name__== '__main__':
	### parser arguments
	import argparse
	from fuzzytools.prints import print_big_bar

	parser = argparse.ArgumentParser('usage description')
	parser.add_argument('-n',  type=int, default=10, help='number of iterations')
	main_args = parser.parse_args()
	print_big_bar()

	###################################################################################################################################################
	import time
	from fuzzytools.progress_bars import ProgressBar, ProgressBarMultiColor
	from fuzzytools.prints import print_bar
	import warnings 

	print_bar()
	bar = ProgressBarMultiColor(main_args.n, ['a', 'b', 'c'], [None, 'red', 'blue'])
	for k in range(main_args.n):
		tdict = {
			'a':str(k)*10,
			'b':str(k)*20,
		}
		bar(tdict)
		warnings.warn('test')
		time.sleep(0.5)

	bar.done()