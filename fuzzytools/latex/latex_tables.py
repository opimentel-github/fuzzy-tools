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
USES_TABULARX = False
VRULE_PT = 10
BLINE_PT = 1.5
CENTERED = False

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
		split_index_names=True,
		key_key_separator:str=KEY_KEY_SEP_CHAR,
		key_value_separator:str=KEY_VALUE_SEP_CHAR,
		bold_function=get_max_elements,
		repr_replace_dict={},
		):
		self.info_df = info_df.copy()
		self.bold_axis = bold_axis
		self.split_index_names = split_index_names
		self.key_key_separator = key_key_separator
		self.key_value_separator = key_value_separator
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
			raise Exception(f'bold_axis={bold_axis}')

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

			sub_txt = sub_txt[:-2] + ' \\tabsrule\\\\'+'\n'
			txt += sub_txt
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
		split_index_names=True,
		key_key_separator:str=KEY_KEY_SEP_CHAR,
		key_value_separator:str=KEY_VALUE_SEP_CHAR,
		delete_redundant_model_keys:bool=True,
		caption:str='?',
		label:str='tab:?',
		centered=CENTERED,
		custom_tabular_align:str=None,
		uses_tabularx=USES_TABULARX,
		vrule_pt=VRULE_PT,
		bline_pt=BLINE_PT,
		bold_function=get_max_elements,
		repr_replace_dict={},
		):
		self.info_dfs = info_dfs
		if not isinstance(info_dfs, list):
			self.info_dfs = [info_dfs]
		assert isinstance(self.info_dfs, list)

		self.sub_latex_tables = [SubLatexTable(info_df,
			bold_axis=bold_axis,
			split_index_names=split_index_names,
			key_key_separator=key_key_separator,
			key_value_separator=key_value_separator,
			bold_function=bold_function,
			repr_replace_dict=repr_replace_dict,
			) for info_df in self.info_dfs]

		### checks
		self.results_columns = self.sub_latex_tables[0].results_columns
		self.new_model_attrs = []
		for sub_latex_table in self.sub_latex_tables:
			assert sub_latex_table.results_columns==self.results_columns
			self.new_model_attrs += list([x for x in sub_latex_table.model_attrs if not x in self.new_model_attrs])

		for sub_latex_table in self.sub_latex_tables:
			sub_latex_table.split_model_key_value_dfs(self.new_model_attrs)

		self.delete_redundant_model_keys = delete_redundant_model_keys
		self.caption = caption
		self.label = label
		self.centered = centered
		self.custom_tabular_align = custom_tabular_align
		self.uses_tabularx = uses_tabularx
		self.vrule_pt = vrule_pt
		self.bline_pt = bline_pt
		self.bold_function = bold_function
		self.repr_replace_dict = repr_replace_dict

		self.split_index_names = split_index_names

	def reset(self):
		pass

	def get_init_txt(self):
		txt = ''
		txt += '\\def\\tabsrule'+'{\\rule{0pt}{'+str(self.vrule_pt)+'pt}\\rule[0pt]{0pt}{0pt}'+'}\n'
		txt += '\\def\\tabbline'+'{'+utils.get_cmidrule(1, len(self.new_model_attrs)+len(self.results_columns), self.bline_pt)+'\\tabsrule}\n'
		txt += '\\begin{table*}[!t]'+'\n' if self.centered else '\\begin{table}[H]'+'\n'
		txt += '\\centering'+'\n'
		txt += '\\caption{'+'\n'+self.caption+'\n'+'}'+'\n'
		txt += '\\label{'+self.label+'}\\vspace{.1cm}'+'\n'
		txt += '\\tiny\\scriptsize\\footnotesize\\small\\normalsize'+'\n'
		txt += '\\normalsize'+'\n'
		tabular_align = utils.get_bar_latex(self.new_model_attrs, self.results_columns) if self.custom_tabular_align is None else self.custom_tabular_align
		txt += '\\begin{tabularx}{\\textwidth}{'+tabular_align+'}'+'\n' if self.uses_tabularx else '\\begin{tabular}{'+tabular_align+'}'+'\n'
		return txt[:-1]

	def get_top_txt(self):
		txt = ''
		txt += '\\tabbline'+'\n'
		txt += ' & '.join([f'{c}' for c in self.new_model_attrs+self.results_columns])+' \\tabsrule\\\\'+'\n'
		txt += utils.get_cmidrule(1, len(self.new_model_attrs))+utils.get_cmidrule(len(self.new_model_attrs)+1, len(self.new_model_attrs)+len(self.results_columns))+'\n'
		return txt[:-1]

	def __repr__(self):
		txt = ''
		txt += self.get_init_txt()+'\n'
		txt += self.get_top_txt()+'\n'
		for sub_latex_table in self.sub_latex_tables:
			txt += str(sub_latex_table)
			txt += '\\tabbline'+'\n'

		txt += self.get_end_txt()+'\n'
		txt = txt.replace(PM_CHAR, '$\\pm$')
		txt = txt.replace(NAN_CHAR, '--')
		txt = txt.replace('%', '\\%')
		txt = strings.get_bar(char='v', init_string='%')+'\n'+txt+strings.get_bar(char='^', init_string='%')+'\n'
		txt = strings.color_str(txt, 'red')
		return txt

	def get_end_txt(self):
		txt = ''
		txt += '\\end{tabularx}'+'\n' if self.uses_tabularx else '\\end{tabular}'+'\n'
		txt += '\\end{table*}'+'\n' if self.centered else '\\end{table}'+'\n'
		return txt[:-1]