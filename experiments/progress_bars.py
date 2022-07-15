#!/usr/bin/env python3
# -*- coding: utf-8 -*
import sys
sys.path.append('../') # or just install the module

###################################################################################################################################################
import argparse
from fuzzytools.prints import print_big_bar

parser = argparse.ArgumentParser(prefix_chars='--')
parser.add_argument('--n',  type=int, default=1000)
main_args = parser.parse_args()
print_big_bar()

###################################################################################################################################################
import time
from fuzzytools.progress_bars import ProgressBar, ProgressBarMultiColor

bar = ProgressBarMultiColor(main_args.n, ['a', 'b', 'c'], [None, 'red', 'blue'])
for k in range(0, main_args.n):
    tdict = {
        'a':str(k)*10,
        'b':str(k)*20,
    }
    bar(tdict)
    time.sleep(0.00001)

bar.done()