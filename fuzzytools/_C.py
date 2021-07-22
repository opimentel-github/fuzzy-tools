import sys
import numpy as np

###################################################################################################################################################

BAR_FULL_MODE = '%(current)d/%(total)d %(bar)s %(percent)3d%% - %(remaining)d remaining - %(string)s'

FILEDIR = '_filedir' # ../../save/data.txt
ROOTDIR = '_rootdir' # ../../save/
FILENAME = '_filename' # data.txt
CFILENAME = '_cfilename' # data
FEXT = '_fext' # txt

KFOLF_CHAR = '@'

FILESIZE_FACTOR = 1e-6 # in mbs

KEY_KEY_SEP_CHAR = '~'
KEY_VALUE_SEP_CHAR = '='

VERBOSE = 0

BAR_SIZE = None # for auto width
JUPYTER_NOTEBOOK_BAR_SIZE = 100
BAR_LAST_CHAR = '>'
MIDDLE_LINE_CHAR = '─'
BOT_SQUARE_CHAR ='▄'
TOP_SQUARE_CHAR = '▀'
BAR_CHAR= '-'
DOBLE_BAR_CHAR = '═'
NAN_CHAR = '─'
PM_CHAR = '±'

DELTA_LATEXCHAR = '$\Delta$'

###################################################################################################################################################
### matplotlib

PLOT_STD_ALPHA = 0.25
PLOT_GRID_ALPHA = 0.25
PLOT_MPLIB_FIGSIZE = (6,4)
PLOT_FIGSIZE = (11,4)
PLOT_FIGSIZE_BOX = (6,4)
PLOT_FIGSIZE_CMAP = (10,8)
PLOT_DPI = 80

AN_LOAD_IMAGE_FEXT = 'jpg'
AN_SAVE_IMAGE_FEXT = 'png'
AN_SEGS_OFFSET = 1

DEFAULT_CMAP = 'cc_favs2'
SAMPLES_TEXT = 'N'

###################################################################################################################################################
### datascience

NAN_VALUE = -999
EPS = 1e-5
CM_FORMAT = np.uint32
STD_LATEXCHAR = '$\sigma$'
SERROR_LATEXCHAR = '$SE$'
N_DECIMALS = 3
REMOVE_ZERO = True
