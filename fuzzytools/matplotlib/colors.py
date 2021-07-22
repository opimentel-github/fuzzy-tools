from __future__ import print_function
from __future__ import division
from . import _C

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

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

NICE_COLORS_DICT = {
'nice_gray':'#4A4A4A',
'nice_black':'#0d0d0d',
'nice_red':'#F24535',
'nice_yellow':'#F2E749',
}

COLORS_DICT = {
###
'seaborn':['#4c72b0', '#dd8452', '#55a868', '#c44e52', '#8172b3', '#937860', '#da8bc3', '#8c8c8c', '#ccb974', '#64b5cd'],
'mplot_default':['#0000ff', '#008000', '#ff0000', '#00c0c0', '#c000c0', '#c0c000', '#000000'],
'mplot_v2':['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'],
'mplot_ggplot':['#E24A33', '#348ABD', '#988ED5', '#777777', '#FBC15E', '#8EBA42', '#FFB5B8'],
'cc_favs':['#F25E5E','#0396A6','#6ABE4F','#B6508A','#F2E749','#404040','#9E2536','#024873','#378A47','#4E2973','#FFD700','#0d0d0d','#008080','#F28963','#F24535',],
'cc_favs2':['#F25E5E','#0396A6','#6ABE4F','#B6508A','#1B9E77','#E7298A','#666666','#0d0d0d','#4E2973','#008080','#F24535','#FFD700'],
###
'cc_black':['#000000', '#696969', '#696969', '#808080', '#808080', '#A9A9A9', '#A9A9A9', '#C0C0C0', '#D3D3D3', '#D3D3D3'],
'cc_red':['#BC8F8F', '#F08080', '#CD5C5C', '#A52A2A', '#B22222', '#800000', '#8B0000', '#FF0000'],
'cc_orange':['#FA8072', '#FF6347', '#E9967A', '#FF7F50', '#FF4500', '#FFA07A', '#A0522D', '#D2691E', '#8B4513', '#F4A460', '#CD853F', '#FF8C00', '#DEB887', '#D2B48C', '#FFDEAD', '#FFA500'],
'cc_yellow':['#F5DEB3', '#B8860B', '#DAA520', '#FFD700', '#F0E68C', '#EEE8AA', '#BDB76B', '#808000', '#FFFF00'],
'cc_green':['#6B8E23', '#9ACD32', '#556B2F', '#ADFF2F', '#7FFF00', '#7CFC00', '#8FBC8F', '#98FB98', '#90EE90', '#228B22', '#32CD32', '#006400', '#008000'],
'cc_blue':['#00BFFF', '#87CEEB', '#87CEFA', '#4682B4', '#1E90FF', '#778899', '#778899', '#708090', '#708090', '#B0C4DE', '#6495ED', '#4169E1', '#191970', '#000080', '#00008B', '#0000CD', '#0000FF'],
'cc_violet':['#6A5ACD', '#483D8B', '#7B68EE', '#9370DB', '#663399', '#8A2BE2', '#4B0082', '#9932CC', '#9400D3', '#BA55D3', '#D8BFD8', '#DDA0DD', '#EE82EE'],
'cc_pink':['#800080', '#8B008B', '#FF00FF', '#FF00FF', '#DA70D6', '#C71585', '#FF1493', '#FF69B4', '#DB7093', '#DC143C', '#FFC0CB', '#FFB6C1'],
'cc_nyra32':['#C04A2F','#D97744','#EBD4AA','#E5A671','#BA6F50','#744039','#3F2831','#9E2636','#E63845','#F47624','#FBAC35','#FBE961','#6ABE4F','#378A47','#225D42','#183D3F','#0D5089','#3291CF','#63CADD','#FFFFFF','#C0CCDD','#8C9BB2','#596887','#3A4566','#ED1B48','#171325','#68376C','#B6508A','#F2757A','#E8B795','#C4876B'],
'cc_viajar':['#F25E5E','#F28963','#04BFAD','#0396A6','#024873'],
'cc_the_guardian':['#4E2973','#4ACAD9','#F2E749','#F24535','#F2F2F2'],
}

def get_colorlist_names():
	return [k for k in COLORS_DICT.keys()]

def colorlist_to_cycled_colorlist(colorlist:list, n:int=None):
	assert isinstance(colorlist, list)
	if n is None:
		new_colorlist = colorlist.copy()
	else:
		cycler = ColorCycler(colorlist)
		cycler = iter(cycler)
		new_colorlist = [next(cycler) for _ in range(n)]
	return [hextofloats(c) for c in new_colorlist]

def colorlist_to_cmap(colorlist:list, name:str='default'):
	cmap = mpl.colors.ListedColormap(colorlist, name=name)
	return cmap

def hextofloats(hex:str, decimals:int=4):
	assert isinstance(hex, str)
	assert hex[0]=='#'
	c = [round(int(hex[i:i + 2], 16) / 255., decimals) for i in (1, 3, 5)]
	return tuple(c)

def get_colorlist(colorlist_name, n:int=None):
	return colorlist_to_cycled_colorlist(COLORS_DICT[colorlist_name], n)

def colors(n:int=None):
	return get_default_colorlist(n)
	
def get_default_colorlist(n:int=None):
	return colorlist_to_cycled_colorlist(COLORS_DICT[_C.DEFAULT_CMAP], n)

def get_nice_colorlist(n:int=None):
	return colorlist_to_cycled_colorlist([NICE_COLORS_DICT[k] for k in NICE_COLORS_DIC.keys()], n)

def get_cmap(colorlist:list,
	cmap_name='cmap',
	):
	cmap = mpl.colors.ListedColormap(colorlist, name=cmap_name)
	return cmap

def get_default_cmap(n:int=None):
	colorlist = get_default_colorlist(n)
	return get_cmap(colorlist, 'default_cpc_cmap')

def palplot(cmap):
	if isinstance(cmap, list):
		cmap = get_cmap(cmap)
	
	n = len(cmap.colors)
	img = np.linspace(0, 1, n)[None,:]
	
	fig, ax = plt.subplots(1,1,figsize=(10,1))
	ax.axis('off')
	ax.set_title(f'{cmap.name} - n: {n}')
	ax.imshow(img, cmap=cmap)
	plt.show()