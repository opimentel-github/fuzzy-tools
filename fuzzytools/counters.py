from __future__ import print_function
from __future__ import division
from . import _C

###################################################################################################################################################

class Counter(object):
	def __init__(self, counter_relation_dict,
		none_value=1e20,
		):
		assert isinstance(counter_relation_dict, dict)
		self.counter_relation_dict = counter_relation_dict.copy()
		self.counter_names = list(counter_relation_dict.keys())
		for cn in self.counter_names:
			if self.counter_relation_dict[cn] is None:
				self.counter_relation_dict[cn] = none_value
			assert self.counter_relation_dict[cn]>=0 # max value
		self.reset()

	def reset(self):
		self.counters_d = {cn:0 for cn in self.counter_names}
		self.global_count = 0

	def update(self):
		self.global_count += 1
		self.counters_d[self.counter_names[0]] += 1
		for k in range(len(self.counter_names)):
			cn0 = self.counter_names[k]
			if self.counters_d[cn0]>self.counter_relation_dict[cn0]:
				self.counters_d[cn0] = 0
				if k<len(self.counter_names)-1:
					cn1 = self.counter_names[k+1]
					self.counters_d[cn1] += 1

	def reset_cn(self, cn):
		self.counters_d[cn] = 0

	def get_global_count(self):
		return self.global_count

	def __getitem__(self, cn):
		return self.counters_d[cn]

	def check(self, cn):
		return self[cn]==self.counter_relation_dict[cn]

	def __repr__(self):
		COUNTER_CHAR = '»'
		txt = COUNTER_CHAR.join([f'{cn}({self.counters_d[cn]:,}/{self.counter_relation_dict[cn]:,})' for cn in self.counter_names])
		#return f'({self.global_count:,}) {txt}'
		return txt