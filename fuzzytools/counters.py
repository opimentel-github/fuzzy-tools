from __future__ import print_function
from __future__ import division
from . import _C

NONE_VALUE = 1e32

###################################################################################################################################################

class Counter(object):
	def __init__(self, counter_relation_dict,
		none_value=NONE_VALUE,
		):
		assert isinstance(counter_relation_dict, dict)
		self.counter_relation_dict = counter_relation_dict.copy()
		self.counter_names = list(counter_relation_dict.keys())
		for counter_name in self.counter_names:
			if self.counter_relation_dict[counter_name] is None:
				self.counter_relation_dict[counter_name] = none_value
			assert self.counter_relation_dict[counter_name]>=0 # max value
		self.reset()

	def reset(self):
		self.counters_d = {counter_name:0 for counter_name in self.counter_names}
		self.global_count = 0

	def update(self):
		self.global_count += 1
		self.counters_d[self.counter_names[0]] += 1
		for k in range(len(self.counter_names)):
			counter_name0 = self.counter_names[k]
			if self.counters_d[counter_name0]>self.counter_relation_dict[counter_name0]:
				self.counters_d[counter_name0] = 0
				if k<len(self.counter_names)-1:
					counter_name1 = self.counter_names[k+1]
					self.counters_d[counter_name1] += 1

	def reset_counter_name(self, counter_name):
		self.counters_d[counter_name] = 0

	def get_global_count(self):
		return self.global_count

	def __getitem__(self, counter_name):
		return self.counters_d[counter_name]

	def check_counter_name_upper_bound(self, counter_name):
		return self[counter_name]==self.counter_relation_dict[counter_name]

	def __repr__(self):
		COUNTER_CHAR = '»'
		txt = COUNTER_CHAR.join([f'{counter_name}({self.counters_d[counter_name]:,}/{self.counter_relation_dict[counter_name]:,})' for counter_name in self.counter_names])
		return txt