from __future__ import print_function
from __future__ import division
from . import _C

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from copy import copy, deepcopy

NICE_GRAY = '#4A4A4A'
NICE_BLACK = '#0d0d0d'
NICE_RED = '#F24535'
NICE_YELLOW = '#F2E749'

SEABORN = ['#4c72b0', '#dd8452', '#55a868', '#c44e52', '#8172b3', '#937860', '#da8bc3', '#8c8c8c', '#ccb974', '#64b5cd']
MPLOT_DEFAULT = ['#0000ff', '#008000', '#ff0000', '#00c0c0', '#c000c0', '#c0c000', '#000000']
MPLOT_V2 = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
MPLOT_GGPLOT = ['#E24A33', '#348ABD', '#988ED5', '#777777', '#FBC15E', '#8EBA42', '#FFB5B8']
CC_FAVS = ['#F25E5E','#0396A6','#6ABE4F','#B6508A','#F2E749','#404040','#9E2536','#024873','#378A47','#4E2973','#FFD700','#0d0d0d','#008080','#F28963','#F24535',]
CC_FAVS2 = ['#0396A6','#F25E5E','#6ABE4F','#B6508A','#1B9E77','#E7298A','#666666','#0d0d0d','#4E2973','#008080','#F24535','#FFD700']
CC_BLACK = ['#000000', '#696969', '#696969', '#808080', '#808080', '#A9A9A9', '#A9A9A9', '#C0C0C0', '#D3D3D3', '#D3D3D3']
CC_RED = ['#BC8F8F', '#F08080', '#CD5C5C', '#A52A2A', '#B22222', '#800000', '#8B0000', '#FF0000']
CC_ORANGE = ['#FA8072', '#FF6347', '#E9967A', '#FF7F50', '#FF4500', '#FFA07A', '#A0522D', '#D2691E', '#8B4513', '#F4A460', '#CD853F', '#FF8C00', '#DEB887', '#D2B48C', '#FFDEAD', '#FFA500']
CC_YELLOW = ['#F5DEB3', '#B8860B', '#DAA520', '#FFD700', '#F0E68C', '#EEE8AA', '#BDB76B', '#808000', '#FFFF00']
CC_GREEN = ['#6B8E23', '#9ACD32', '#556B2F', '#ADFF2F', '#7FFF00', '#7CFC00', '#8FBC8F', '#98FB98', '#90EE90', '#228B22', '#32CD32', '#006400', '#008000']
CC_BLUE = ['#00BFFF', '#87CEEB', '#87CEFA', '#4682B4', '#1E90FF', '#778899', '#778899', '#708090', '#708090', '#B0C4DE', '#6495ED', '#4169E1', '#191970', '#000080', '#00008B', '#0000CD', '#0000FF']
CC_VIOLET = ['#6A5ACD', '#483D8B', '#7B68EE', '#9370DB', '#663399', '#8A2BE2', '#4B0082', '#9932CC', '#9400D3', '#BA55D3', '#D8BFD8', '#DDA0DD', '#EE82EE']
CC_PINK = ['#800080', '#8B008B', '#FF00FF', '#FF00FF', '#DA70D6', '#C71585', '#FF1493', '#FF69B4', '#DB7093', '#DC143C', '#FFC0CB', '#FFB6C1']
CC_NYRA32 = ['#C04A2F','#D97744','#EBD4AA','#E5A671','#BA6F50','#744039','#3F2831','#9E2636','#E63845','#F47624','#FBAC35','#FBE961','#6ABE4F','#378A47','#225D42','#183D3F','#0D5089','#3291CF','#63CADD','#FFFFFF','#C0CCDD','#8C9BB2','#596887','#3A4566','#ED1B48','#171325','#68376C','#B6508A','#F2757A','#E8B795','#C4876B']
CC_VIAJAR = ['#F25E5E','#F28963','#04BFAD','#0396A6','#024873']
CC_THE_GUARDIAN = ['#4E2973','#4ACAD9','#F2E749','#F24535','#F2F2F2']

DEFAULT_CMAP = CC_FAVS2
NOF_DECIMALS = 10

###################################################################################################################################################

def plt_color(color,
	figsize=(1,1),
	dpi=200,
	n=10,
	):
	img = np.linspace(0, 1, n)[None,:]
	fig, ax = plt.subplots(1, 1, figsize=figsize, dpi=dpi)
	ax.axis('off')
	hexcolor = get_hexcolor(color)
	rbgcolor = get_rgbcolor(color)
	ax.set_title(f'hexcolor={hexcolor}; rbgcolor={rbgcolor}')
	cmap = colorlist2cmap([color])
	ax.imshow(img, cmap=cmap)
	plt.show()

###################################################################################################################################################

def get_color_format(color):
	if (
		type(color)==list and
		len(color)==3 and
		all([(c>=0 and c<=1) for c in color])
		):
		return 'rgb'
	elif (
		type(color)==str and
		color[0]=='#' and
		len(color)==7
		):
		return 'hex'
	else:
		raise Exception(f'color={color}')

def get_rgbcolor(color):
	color_format = get_color_format(color)
	if color_format=='rgb':
		return color
	elif color_format=='hex':
		rgbcolor = [round(int(color[i:i + 2], 16) / 255., NOF_DECIMALS) for i in (1, 3, 5)]
		return rgbcolor
	else:
		raise Exception(f'color_format={color_format}')

def get_hexcolor(color):
	color_format = get_color_format(color)
	if color_format=='rgb':
		tuple_color = tuple([int(c*255) for c in color])
		hexcolor = '#%02x%02x%02x'%tuple_color
		return hexcolor
	elif color_format=='hex':
		return color
	else:
		raise Exception(f'color_format={color_format}')

def get_scaled_rgbcolor(rgbcolor, scale):
	new_rgbcolor = [min(1, x*scale) for x in rgbcolor]
	return new_rgbcolor

def get_scaled_color(color, scale):
	assert scale>=0
	color_format = get_color_format(color)
	rgbcolor = get_rgbcolor(color)
	new_rgbcolor = get_scaled_rgbcolor(rgbcolor, scale)
	new_color = globals()[f'get_{color_format}color'](new_rgbcolor) # convert to original color format
	return new_color

###################################################################################################################################################

class ColorCycler:
	def __init__(self, colors):
		self.colors = colors
		self.index = 0
		
	def __iter__(self):
		self.index = 0
		return self

	def __next__(self):
		if self.index < len(self.colors):
			x = self.colors[self.index]
			self.index += 1
			return x
		else:
			self.index = 0
			return next(self)

def colorlist_to_cycled_colorlist(colorlist:list,
	n:int=None,
	):
	assert n is None or n>0
	assert type(colorlist)==list
	if n is None:
		new_colorlist = colorlist.copy()
	else:
		cycler = ColorCycler(colorlist)
		cycler = iter(cycler)
		new_colorlist = [next(cycler) for _ in range(n)]
	return new_colorlist

###################################################################################################################################################

def colorlist2cmap(colorlist:list,
	cmap_name='cmap_name',
	):
	cmap = mpl.colors.ListedColormap(colorlist, name=cmap_name)
	return cmap

def get_default_colorlist(
	n:int=None,
	):
	default_colorlist = colorlist_to_cycled_colorlist(DEFAULT_CMAP,
		n=n,
		)
	return default_colorlist

def get_default_cmap(
	n:int=None,
	cmap_name='cmap_name',
	):
	colorlist = get_default_colorlist(
		n=n,
		)
	default_cmap = colorlist2cmap(colorlist,
		cmap_name='default_cpc_cmap',
		)
	return default_cmap

###################################################################################################################################################

def get_color_dict(_obj_names,
	colorlist=DEFAULT_CMAP,
	sorts=True,
	):
	obj_names = deepcopy(_obj_names)
	if sorts:
		obj_names.sort()
	new_colorlist = colorlist_to_cycled_colorlist(colorlist, len(obj_names))
	d = {}
	for k,obj_name in enumerate(obj_names):
		assert type(obj_name)==str
		d[obj_name] = new_colorlist[k]
	return d