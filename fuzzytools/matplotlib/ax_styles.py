from __future__ import print_function
from __future__ import division
from . import C_

import matplotlib.pyplot as plt
import numpy as np

###################################################################################################################################################

def set_color_borders(ax, c,
	linewidth=2,
	):
	[ax.spines[border].set_color(c) for border in ['bottom', 'top', 'right', 'left']]
	[ax.spines[border].set_linewidth(linewidth) for border in ['bottom', 'top', 'right', 'left']]