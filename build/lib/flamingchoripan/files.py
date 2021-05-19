from __future__ import print_function
from __future__ import division
from . import C_

import pickle
import os
from . import strings
from . import prints

###################################################################################################################################################

def get_filesize(filedir:str):
	return os.path.getsize(filedir)*C_.FILESIZE_FACTOR

def check_filedir_exists(filedir:str):
	return os.path.isfile(filedir)

def delete_filedirs(filedirs:list,
	verbose=1,
	):
	return sum([delete_filedir(filedir, verbose) for filedir in filedirs])>0

def delete_filedir(filedir:str,
	verbose=1,
	):
	deleted = False
	if not filedir is None:
		if os.path.exists(filedir):
			if verbose==1:
				prints.print_red(f'> deleting: {filedir}')
			os.remove(filedir)
			deleted = True

	return deleted

def save_pickle(filedirs:str, obj:object,
	uses_create_dir:bool=True,
	verbose=1,
	):
	'''
	Parameters
	----------
	filedir: filedir of file to save
	obj: object to save. Be careful with cuda serialized objects
	'''
	if isinstance(filedirs, str):
		filedirs = [filedirs]
	for filedir in filedirs:
		save_pickle_(filedir, obj,
		uses_create_dir,
		verbose,
		)

def save_pickle_(filedir:str, obj:object,
	uses_create_dir:bool=True,
	verbose=1,
	):
	'''
	Parameters
	----------
	filedir: filedir of file to save
	obj: object to save. Be careful with cuda serialized objects
	'''
	assert isinstance(filedir, str)
	if verbose==1:
		prints.print_green(f'> saving: {filedir}')
	
	if uses_create_dir:
		create_dir('/'.join(filedir.split('/')[:-1]), verbose=int(verbose==2))

	file_pi = open(filedir, 'wb')
	pickle.dump(obj, file_pi)
	file_pi.close()
	
def load_pickle(filedir:str,
	return_filesize:bool=False,
	verbose=1,
	):
	'''
	Parameters
	----------
	filedir: filedir of file to read

	Return
	----------
	obj (object): the read object from disk
	'''
	if filedir is None:
		return None

	if verbose==1:
		prints.print_blue(f'> loading: {filedir}')

	pickle_in = open(filedir,'rb')
	obj = pickle.load(pickle_in)
	pickle_in.close()

	if return_filesize:
		return obj, get_filesize(filedir)
	else:
		return obj

def get_filedirs(rootdir:str,
	fext:str=None,
	):
	'''
	Get a list of filedirs in all subdirs with extention .fext

	Parameters
	----------
	rootdir: start path to search
	fext: file extention. None: search for all extentions
	
	Return
	----------
	filedirs (list[srt]): list of filedirs
	'''
	filedirs = []
	for root, dirs, files in os.walk(rootdir):
		level = root.replace(rootdir, '').count(os.sep)
		indent = ' ' * 4 * (level)+'> '
		subindent = ' ' * 4 * (level + 1)+'- '
		for f in files:
			if (fext is None) or (f.split('.')[-1]==fext): # dont add if none
				filedirs.append(f'{root}/{f}')
			
	return filedirs

def get_dict_from_filedir(filedir:str,
	key_key_separator:str=C_.KEY_KEY_SEP_CHAR,
	key_value_separator:str=C_.KEY_VALUE_SEP_CHAR,
	):
	splits = filedir.split('/')
	ret_dict = {
		C_.FILEDIR:filedir,
		C_.ROOTDIR:'/'.join(splits[:-1]),
		C_.FILENAME:'.'.join(splits[-1].split('.')),
		C_.CFILENAME:'.'.join(splits[-1].split('.')[:-1]),
		C_.FEXT:splits[-1].split('.')[-1],
	}
	ret_dict.update(strings.get_dict_from_string(ret_dict[C_.CFILENAME], key_key_separator=key_key_separator , key_value_separator=key_value_separator))
	return ret_dict

def search_for_filedirs(rootdir:str,
	string_query:list=[''],
	string_filter:list=[],
	fext:str=None,
	verbose:int=1,
	sort:bool=False,
	):
	'''
	Get a list of filedirs in all subdirs with extention .fext.
	Also, uses filters of key strings.

	Parameters
	----------
	rootdir (srt): start path to search
	string_query (list[srt]): (optional) list with string queries that have to appear in all the cfilenames.
	string_filter(list[str]): (optional) list with string queries that don't have to appear in all the cfilenames.
	fext (srt): (optional) file extention. Default is None: search for all extentions
	verbose (int): verbosity of method

	Return
	----------
	filesret (list[srt]): list of filedirs that meet the conditions
	'''
	PrintC = prints.ShowPrints if verbose>0 else prints.HiddenPrints
	with PrintC():
		prints.print_bar()
		filedirs = get_filedirs(rootdir, fext=fext)
		print(f'found filedirs: ({rootdir})')
		for k,filedir in enumerate(filedirs):
			filesize = get_filesize(filedir)
			print(f'({k}) - {filedir} - {filesize:.3f}[mbs]')
				
		if sort:
			filedirs.sort(key=str.lower)

		filedirs_res = []
		for filedir in filedirs:
			filedict = get_dict_from_filedir(filedir)
			cfilename = filedict[C_.CFILENAME]
			if strings.query_strings_in_string(string_query, cfilename) and not strings.query_strings_in_string(string_filter, cfilename):
				filedirs_res.append(filedir)

		prints.print_bar()
		print(f'filedirs after searching with filters: ({rootdir})')
		for k,filedir in enumerate(filedirs_res):
			filesize = get_filesize(filedir)
			print(f'({k}) - {filedir} - {filesize:.3f}[mbs]')
		prints.print_bar()
	return filedirs_res

def get_filedir_count(filedir:str,
	fext:str=None,
	):
	'''
	return the count of filenames with an extention .fext
	'''
	return len(get_filedirs(filedir, fext=fext))

def get_cfilename(filedir:str):
	return get_dict_from_filedir(filedir)[C_.CFILENAME]

def print_all_filedirs(filedir:str='.'):
	print(f'total files in {filedir}: {get_filedir_count(filedir)}')
	for root, dirs, files in os.walk(filedir):
		level = root.replace(filedir, '').count(os.sep)
		indent = ' ' * 4 * (level)+'> '
		print(f'{indent}{os.path.basename(root)}/')
		subindent = ' ' * 4 * (level + 1)+'- '
		for f in files:
			print(f'{subindent}{f}')

def create_dir(new_dir:str,
	iterative:bool=True,
	verbose:int=1,
	):
	if verbose==1 and not os.path.exists(new_dir):
		prints.print_yellow(f'> creating dir: {new_dir}')

	if iterative:
		create_dir_iterative(new_dir, verbose=int(verbose==2))
	else:
		create_dir_individual(new_dir, verbose=int(verbose==2))


def create_dir_individual(new_dir:str,
	verbose:int=0,
	):
	'''
	check if dir already exists
	'''
	if not os.path.exists(new_dir):
		if verbose==1:
			prints.print_yellow(f'>> creating dir: {new_dir}')
		os.mkdir(new_dir)
	else:
		# already exits
		pass
		
def create_dir_iterative(new_dir:str,
	verbose:int=0,
	):
	dirs = new_dir.split('/')
	new_dir = ''
	for f in dirs:
		new_dir += f+'/'
		create_dir_individual(new_dir, verbose=verbose)
