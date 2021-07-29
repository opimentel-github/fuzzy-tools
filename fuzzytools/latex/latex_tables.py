from __future__ import print_function
from __future__ import division
from . import _C

import copy
import pandas as pd
import numpy as np
from .. import strings as strings
from . import utils as utils
from ..lists import get_max_elements
from ..dataframes import DFBuilder

KEY_KEY_SEP_CHAR = _C.KEY_KEY_SEP_CHAR
KEY_VALUE_SEP_CHAR = _C.KEY_VALUE_SEP_CHAR
NAN_CHAR = _C.NAN_CHAR
PM_CHAR = _C.PM_CHAR

###################################################################################################################################################

class SubLatexTable():
	'''
	Class used to convert a dataframe of model results and experiments in a latex string to just copy-paste in overleaf.
	This class can bold the best result along a column (experiment) given a criterium: maximum or minimum.
	Also, you can use the XError class from ..datascience.statistics

	The format of the table is:
	------------------------------------------------------------------------------------------------------------
	model_att_1, model_value_1, model_att_2, model_value_2, ... | experiment_1, experiment_2, experiment_3, ...
	------------------------------------------------------------------------------------------------------------
	A1           a1             X1           x1                 | Xerror()     				...
	B1           b1             Y1           y1                 | Xerror()     ...
	C1           c1             Z1           z1                 | Xerror()     ...
	------------------------------------------------------------------------------------------------------------
	'''
	def __init__(self, info_df,
		bold_axis:list=None,
		rule_ab:tuple=(2, 1),
		split_index_names=True,
		key_key_separator:str=KEY_KEY_SEP_CHAR,
		key_value_separator:str=KEY_VALUE_SEP_CHAR,
		hline_k=None,
		bold_function=get_max_elements,
		repr_replace_dict={},
		):
		self.info_df = info_df.copy()
		self.bold_axis = bold_axis
		self.rule_ab = rule_ab
		self.split_index_names = split_index_names
		self.key_key_separator = key_key_separator
		self.key_value_separator = key_value_separator
		self.hline_k = hline_k
		self.bold_function = bold_function
		self.repr_replace_dict = repr_replace_dict
		self.reset()

	def reset(self):
		self.results_columns = list(self.info_df.columns)
		self.set_bold_df()
		self.split_model_key_value_dfs()

	def set_bold_df(self):
		columns = list(self.info_df.columns)
		indexs = self.info_df.index
		#print('info_df',self.info_df)
		if self.bold_axis is None:
			bold_df = None

		elif self.bold_axis=='rows':
			bold_df = DFBuilder()
			for k,row in enumerate(self.info_df.iterrows()):
				index = indexs[k]
				values = row[1].values
				bold_values = self.bold_function(values)
				bold_df.append(index, {c:bold_values[kc] for kc,c in enumerate(columns)})
			bold_df = bold_df()

		elif self.bold_axis=='columns':
			max_values_d = {}
			for c in columns:
				values = self.info_df[c].values
				bold_values = self.bold_function(values)
				max_values_d[c] = bold_values

			bold_df = DFBuilder()
			for k,row in enumerate(self.info_df.iterrows()):
				index = indexs[k]
				bold_df.append(index, {c:max_values_d[c][k] for kc,c in enumerate(columns)})
			bold_df = bold_df()

		else:
			raise Exception(f'No mode {bold_axis}')

		#print('bold_df',bold_df)
		self.bold_df = bold_df

	def split_model_key_value_dfs(self,
		model_attrs=None,
		):
		if not self.split_index_names:
			pass
		else:
			if model_attrs is None:
				self.model_attrs = []
				indexs = self.info_df.index.values
				for k,index in enumerate(indexs):
					d = strings.get_dict_from_string(index, self.key_key_separator, self.key_value_separator)
					self.model_attrs += [x for x in d.keys() if not x in self.model_attrs]
			else:
				self.model_attrs = model_attrs.copy()

			mdl_info_dict = {}
			indexs = self.info_df.index.values
			for k,index in enumerate(indexs):
				d = strings.get_dict_from_string(index, self.key_key_separator, self.key_value_separator)
				mdl_info_dict[index] = {k:d.get(k, None) for k in self.model_attrs}

			self.mdl_info_df = pd.DataFrame.from_dict(mdl_info_dict, orient='index').reindex(list(mdl_info_dict.keys()))
			self.mdl_info_df = self.mdl_info_df.fillna(NAN_CHAR)
			self.new_info_df = pd.concat([self.mdl_info_df, self.info_df], axis=1)

	def __repr__(self):
		txt = ''
		hline_c = 0
		for k,row in enumerate(self.new_info_df.iterrows()):
			#print('row',row[1].values)
			values = row[1].values
			#print('values',values)
			sub_txt = ''
			for kv,v in enumerate(values):
				if any([isinstance(v, int), isinstance(v, float)]):
					v_str = strings.xstr(v)
				else:
					v_str = str(v)
				model_attrs = len(values)-len(self.results_columns)
				kvv = kv-model_attrs
				is_bold =  False if kvv<0 or self.bold_df is None else self.bold_df.values[k,kvv]
				sub_txt += '\\textbf{'+v_str+'}' if is_bold else v_str
				sub_txt += ' & '

			sub_txt = sub_txt[:-2] + f' {utils.get_slash()}srule{utils.get_dslash()}'+'\n'
			txt += sub_txt
			if not self.hline_k is None:
				if hline_c>=self.hline_k and k<len(self.row_colors)-1:
					txt += utils.get_hline()+'\n'
					hline_c = 0
				else:
					hline_c += 1

		txt = strings.string_replacement(txt, self.repr_replace_dict)
		return txt

###################################################################################################################################################

class LatexTable():
	'''
	Class used to convert a dataframe of model results and experiments in a latex string to just copy-paste in overleaf.
	This class can bold the best result along a column (experiment) given a criterium: maximum or minimum.
	Also, you can use the XError class from ..datascience.statistics
	You can use subtables, each one with local independent criteriums separated by an horizontal line.

	The format of the table is:
	------------------------------------------------------------------------------------------------------------
	model_att_1, model_value_1, model_att_2, model_value_2, ... | experiment_1, experiment_2, experiment_3, ...
	------------------------------------------------------------------------------------------------------------
	A1           a1             X1           x1                 | Xerror()     				...
	B1           b1             Y1           y1                 | Xerror()     ...
	C1           c1             Z1           z1                 | Xerror()     ...
	------------------------------------------------------------------------------------------------------------
	A2           a2             X2           x2                 | Xerror()     ...
	B2           b2             Y2           y2                 | Xerror()     ...
	C2           c2             Z2           z2                 | Xerror()     ...
	------------------------------------------------------------------------------------------------------------
	'''
	def __init__(self, info_dfs:list,
		bold_axis:list=None,
		rule_ab:tuple=(2, 1),
		split_index_names=True,
		key_key_separator:str=_C.KEY_KEY_SEP_CHAR,
		key_value_separator:str=_C.KEY_VALUE_SEP_CHAR,
		delete_redundant_model_keys:bool=True,
		caption:str='',
		label:str='.tab',
		centered:bool=False,
		custom_tabular_align:str=None, # 'ccc|llll'
		hline_k=None,
		bold_function=get_max_elements,
		repr_replace_dict={},
		):
		self.info_dfs = info_dfs
		if not isinstance(info_dfs, list):
			self.info_dfs = [info_dfs]
		assert isinstance(self.info_dfs, list)

		self.sub_latex_tables = [SubLatexTable(info_df,
			bold_axis,
			rule_ab,
			split_index_names,
			key_key_separator,
			key_value_separator,
			hline_k,
			bold_function,
			repr_replace_dict,
			) for info_df in self.info_dfs]

		### checks
		self.results_columns = self.sub_latex_tables[0].results_columns
		self.new_model_attrs = []
		for sub_latex_table in self.sub_latex_tables:
			assert sub_latex_table.results_columns==self.results_columns
			self.new_model_attrs += list([x for x in sub_latex_table.model_attrs if not x in self.new_model_attrs])

		for sub_latex_table in self.sub_latex_tables:
			#print(self.new_model_attrs)
			sub_latex_table.split_model_key_value_dfs(self.new_model_attrs)

		self.delete_redundant_model_keys = delete_redundant_model_keys
		self.caption = caption
		self.label = label
		self.centered = centered
		self.custom_tabular_align = custom_tabular_align
		self.hline_k = hline_k
		self.bold_function = bold_function
		self.repr_replace_dict = repr_replace_dict

		self.rule_ab = rule_ab
		self.split_index_names = split_index_names

	def reset(self):
		pass

	def get_init_txt(self):
		txt = ''
		txt += f'{utils.get_slash()}def{utils.get_slash()}srule'+'{'+utils.get_rule(*self.rule_ab)+'}\n'
		txt += utils.get_slash()+'begin{table*}\n' if self.centered else utils.get_slash()+'begin{table}[H]\n'
		txt += utils.get_slash()+'centering'+'\n'
		txt += utils.get_slash()+'caption{'+'\n'+self.caption+'\n'+'}'+'\n'
		txt += utils.get_slash()+'label{'+self.label+'}'+utils.get_slash()+'vspace{.1cm}'+'\n'
		txt += '\\tiny\\scriptsize\\footnotesize\\small\\normalsize'+'\n'
		tabular_align = utils.get_bar_latex(self.new_model_attrs, self.results_columns) if self.custom_tabular_align is None else self.custom_tabular_align
		txt += utils.get_slash()+'begin{tabularx}{\\textwidth}{'+tabular_align+'}'+'\n'
		return txt[:-1]

	def get_top_txt(self):
		txt = utils.get_hline()+'\n'
		txt += ' & '.join([f'{c}' for c in self.new_model_attrs+self.results_columns])+f' {utils.get_slash()}srule{utils.get_dslash()}'+'\n'
		# txt += f'{utils.get_hline()+utils.get_hline()}'+'\n'
		txt += '\\hlineB{4}'+'\n'
		return txt[:-1]

	def __repr__(self):
		txt = ''
		txt += self.get_init_txt()+'\n'
		txt += self.get_top_txt()+'\n'
		for sub_latex_table in self.sub_latex_tables:
			txt += str(sub_latex_table)
			txt += utils.get_hline()+'\n'

		txt += self.get_end_txt()+'\n'
		txt = txt.replace(PM_CHAR, f'${utils.get_slash()}pm$')
		txt = txt.replace(NAN_CHAR, '$-$')
		txt = txt.replace('%', utils.get_slash()+'%')
		txt = strings.get_bar(char='%')+'\n'+txt+strings.get_bar(char='%')+'\n'
		txt = strings.color_str(txt, 'red')
		return txt

	def get_end_txt(self):
		txt = ''
		txt += '\\end{tabularx}'+'\n'
		txt += '\\end{table*}'+'\n' if self.centered else '\\end{table}'+'\n'
		return txt[:-1]