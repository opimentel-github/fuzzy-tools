from __future__ import print_function
from __future__ import division
from . import C_

import copy
import pandas as pd
import numpy as np
from .. import strings as strings
from . import utils as utils
from ..datascience import statistics as fstats

###################################################################################################################################################

def get_bar_latex(model_attributes:int, results:int):
	'''
	Return a latex table align format string.
	Ej: lcc|ccccc
	The bar is used to separate the model attributes from the results
	'''
	bar = 'l'+'c'*(model_attributes-1)+'|'+'c'*(results)
	return bar

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
		bold_criteriums:list=None,
		replace_dic:dict={},
		colored_criterium_row:bool=True,
		rule_ab:tuple=(2, 1),
		split_index_names=True,
		key_key_separator:str=C_.KEY_KEY_SEP_CHAR,
		key_value_separator:str=C_.KEY_VALUE_SEP_CHAR,
		):
		self.res_info_df = info_df
		self.rule_ab = rule_ab
		self.split_index_names = split_index_names
		self.key_key_separator = key_key_separator
		self.key_value_separator = key_value_separator
		self.results_columns = list(self.res_info_df.columns)
		self.set_bold_criteriums(bold_criteriums)
		self.reset()

	def reset(self,
		model_attrs=None,
		):
		self.set_row_colors()
		self.split_model_key_value_dfs(model_attrs)
		#print(self.bold_criteriums)
		#print(self.res_info_df)
		#print(self.mdl_info_df)
		#print(self.info_df)

	def set_bold_criteriums(self, bold_criteriums):
		if bold_criteriums is None:
			bold_criteriums = {rc:None for rc in self.results_columns}
		elif isinstance(bold_criteriums, str):
			bold_criteriums = {rc:bold_criteriums for rc in self.results_columns}

		assert isinstance(bold_criteriums, dict)
		for rc in self.results_columns:
			bc = bold_criteriums[rc]
			assert bc is None or isinstance(bc, str)
		self.bold_criteriums = bold_criteriums

	def set_row_colors(self):
		#self.row_colors = ['' if row_colors[index] is None else f'\\rowcolor[HTML]{utils.brackets(row_colors[index][1:])}' for k in range(len(self.res_info_df))]
		self.row_colors = ['' for k in range(len(self.res_info_df))]

	def split_model_key_value_dfs(self,
		model_attrs=None,
		):
		if not self.split_index_names:
			pass
		else:
			if model_attrs is None:
				self.model_attrs = []
				indexs = self.res_info_df.index.values
				for k,index in enumerate(indexs):
					d = strings.get_dict_from_string(index, self.key_key_separator, self.key_value_separator)
					self.model_attrs += [x for x in d.keys() if not x in self.model_attrs]
			else:
				self.model_attrs = model_attrs.copy()

			mdl_info_dict = {}
			indexs = self.res_info_df.index.values
			for k,index in enumerate(indexs):
				d = strings.get_dict_from_string(index, self.key_key_separator, self.key_value_separator)
				mdl_info_dict[index] = {k:d.get(k, None) for k in self.model_attrs}

			self.mdl_info_df = pd.DataFrame.from_dict(mdl_info_dict, orient='index').reindex(list(mdl_info_dict.keys()))
			self.mdl_info_df = self.mdl_info_df.fillna(C_.NAN_CHAR)
			self.info_df = pd.concat([self.mdl_info_df, self.res_info_df], axis=1)

	def __repr__(self):
		txt = ''
		for row,row_color in zip(self.info_df.iterrows(), self.row_colors):
			#print('row',row[1].values)
			#txt += row_color+' & '.join([row[c] for c in self.model_keys]+[row[c].__repr__() for c in self.results_columns])+' \\\\'
			values = row[1].values
			sub_txt = ''
			for kv,v in enumerate(values):
				v_str = str(v) if isinstance(v, fstats.XError) else strings.xstr(v)
				model_attrs = len(values)-len(self.results_columns)
				if kv>=model_attrs and not isinstance(v, str):
					to_compare = [row[1].values[kv] for row in self.info_df.iterrows()]
					#print(v,to_compare,max(to_compare))
					bold_criterium = self.bold_criteriums[self.results_columns[kv-model_attrs]]
					if bold_criterium is None:
						pass
					elif bold_criterium=='min':
						v_str = utils.get_bold(v_str) if v==min(to_compare) else v_str
					elif bold_criterium=='max':
						v_str = utils.get_bold(v_str) if v==max(to_compare) else v_str
					else:
						raise Exception(f'invalid bold_criterium {bold_criterium}')
				sub_txt += v_str
				sub_txt += ' & '

			sub_txt = row_color + sub_txt[:-2] + f' {utils.get_slash()}srule{utils.get_dslash()}'+'\n'
			txt += sub_txt
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
		bold_criteriums:list=None,
		replace_dic:dict={},
		colored_criterium_row:bool=True,
		rule_ab:tuple=(2, 1),
		split_index_names=True,
		key_key_separator:str=C_.KEY_KEY_SEP_CHAR,
		key_value_separator:str=C_.KEY_VALUE_SEP_CHAR,

		delete_redundant_model_keys:bool=True,
		caption:str='???',
		label:str='???',
		centered:bool=True,
		custom_tabular_align:str=None, # 'ccc|llll'
		):
		self.info_dfs = info_dfs
		if not isinstance(info_dfs, list):
			self.info_dfs = [info_dfs]
		assert isinstance(self.info_dfs, list)

		self.sub_latex_tables = [SubLatexTable(info_df,
			bold_criteriums,
			replace_dic,
			colored_criterium_row,
			rule_ab,
			split_index_names,
			key_key_separator,
			key_value_separator,
			) for info_df in self.info_dfs]

		### checks
		self.results_columns = self.sub_latex_tables[0].results_columns
		self.new_model_attrs = []
		for sub_latex_table in self.sub_latex_tables:
			assert sub_latex_table.results_columns==self.results_columns
			self.new_model_attrs += list([x for x in sub_latex_table.model_attrs if not x in self.new_model_attrs])

		for sub_latex_table in self.sub_latex_tables:
			#print(self.new_model_attrs)
			sub_latex_table.reset(self.new_model_attrs)

		self.delete_redundant_model_keys = delete_redundant_model_keys
		self.caption = caption
		self.label = label
		self.centered = centered
		self.custom_tabular_align = custom_tabular_align
		self.rule_ab = rule_ab
		self.split_index_names = split_index_names

	def get_init_txt(self):
		txt = ''
		txt += f'{utils.get_slash()}def{utils.get_slash()}srule'+'{'+utils.get_rule(*self.rule_ab)+'}\n'
		txt += utils.get_slash()+'begin{table*}\n' if self.centered else utils.get_slash()+'begin{table}[H]\n'
		txt += utils.get_slash()+'centering'+'\n'
		txt += utils.get_slash()+'caption{'+self.caption+'}'+'\n'
		txt += utils.get_slash()+'label{'+self.label+'}'+utils.get_slash()+'vspace{.1cm}'+'\n'
		tabular_align = utils.get_bar_latex(self.new_model_attrs, self.results_columns) if self.custom_tabular_align is None else self.custom_tabular_align
		txt += utils.get_slash()+'begin{tabular}{'+tabular_align+'}'
		return txt

	def get_top_txt(self):
		txt = utils.get_hline()+'\n'
		txt += ' & '.join([f'{c}' for c in self.new_model_attrs+self.results_columns])+f' {utils.get_slash()}srule{utils.get_dslash()}{utils.get_hline()+utils.get_hline()}'
		return txt

	def __repr__(self):
		txt = ''
		txt += self.get_init_txt()+'\n'
		txt += self.get_top_txt()+'\n'
		for sub_latex_table in self.sub_latex_tables:
			txt += str(sub_latex_table)
			txt += utils.get_hline()+'\n'
			#txt += '\n'

		txt += self.get_end_txt()
		txt = txt.replace(C_.PM_CHAR, f'${utils.get_slash()}pm$')
		txt = txt.replace(C_.NAN_CHAR, '$-$')
		txt = txt.replace('%', utils.get_slash()+'%')
		txt = strings.get_bar(char='%')+'\n'+txt+strings.get_bar(char='%')+'\n'
		return strings.color_str(txt, 'red')
		#return txt

	def get_end_txt(self):
		txt = ''
		txt += '\\end{tabular}'+'\n'
		txt += '\\end{table*}'+'\n' if self.centered else '\\end{table}'+'\n'
		return txt