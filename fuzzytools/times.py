from __future__ import print_function
from __future__ import division
from . import _C

import os
import time
from .strings import xstr
import datetime

###################################################################################################################################################

def get_date_hour():
	date, hour = str(datetime.datetime.now()).split(' ')
	return date, hour

###################################################################################################################################################

class Cronometer(object):
	def __init__(self):
		self.reset()

	def get_time(self):
		return time.perf_counter() # in segs
		#return time.thread_time() # in segs
		#return time.process_time() # in segs

	def reset(self):
		self.it_pt = self.get_time()
		self.last_dt = 0

	def dt_mins(self,
		reset:bool=False,
		):
		return self.dt_segs(reset)/60.

	def dt_segs(self,
		reset:bool=False,
		):
		dt = self.get_time()-self.it_pt
		self.last_dt = dt
		if reset:
			self.reset()
		return dt

	def dt(self,
		reset:bool=False,
		):
		return self.dt_segs(reset)

	def __repr__(self):
		dt = self.dt_segs()
		#dt = self.last_dt
		#txt = f'dt: {dt:.3f}[segs] {dt/60.:.3f}[mins] {dt/60./60.:.3f}[hrs]'
		#txt = f'©{xstr(dt, n_decimals=3)}[segs]'
		txt = f'<dt={xstr(dt, n_decimals=3)}s>'
		return txt