from __future__ import print_function
from __future__ import division
from . import _C

import pickle
import os
import time 
from . import strings
from . import prints
from . import lists
from nested_dict import nested_dict
from .times import get_date_hour
from shutil import copyfile

KEY_KEY_SEP_CHAR = _C.KEY_KEY_SEP_CHAR
KEY_VALUE_SEP_CHAR = _C.KEY_VALUE_SEP_CHAR
KFOLF_CHAR = _C.KFOLF_CHAR
FILEDIR = '_filedir' # ../../save/data.txt
ROOTDIR = '_rootdir' # ../../save/
FILENAME = '_filename' # data.txt
CFILENAME = '_cfilename' # data
FEXT = '_fext' # txt
FILESIZE_FACTOR = 1e-6 # in mbs
VERBOSE = 0
IMBALANCED_KF_MODE = 'error' # error ignore oversampling
RANDOM_STATE = None

###################################################################################################################################################

def filedir_exists(filedir:str):
	return os.path.isfile(filedir)

def path_exists(rootdir:str):
	return os.path.isdir(rootdir)

def get_filesize(filedir:str):
	return os.path.getsize(filedir)*FILESIZE_FACTOR if filedir_exists(filedir) else None # in mb

###################################################################################################################################################

def delete_filedirs(filedirs:list,
	verbose=VERBOSE,
	):
	all_success = sum([delete_filedir(filedir, verbose) for filedir in filedirs])>0
	return all_success

def delete_filedir(filedir:str,
	verbose=VERBOSE,
	):
	success = False
	if not filedir is None:
		if filedir_exists(filedir):
			if verbose==1:
				prints.print_red(f'> deleting: {filedir}')
			os.remove(filedir)
			success = True

	return success

def copy_filedir(src_filedir, dst_filedir):
	if src_filedir==dst_filedir:
		return False
	copyfile(src_filedir, dst_filedir)
	return True

###################################################################################################################################################

def create_dir(new_dir:str,
	iterative:bool=True,
	verbose:int=VERBOSE,
	):
	if path_exists(new_dir):
		return
		
	if verbose==1:
		prints.print_yellow(f'> creating dir: {new_dir}')

	if iterative:
		create_dir_iterative(new_dir, verbose=int(verbose==2))
	else:
		create_dir_individual(new_dir, verbose=int(verbose==2))
	return


def create_dir_individual(new_dir:str,
	verbose:int=VERBOSE,
	):
	if path_exists(new_dir):
		return

	if verbose==1:
		prints.print_yellow(f'>> creating dir: {new_dir}')
	os.mkdir(new_dir)
		
def create_dir_iterative(new_dir:str,
	verbose:int=VERBOSE,
	):
	if path_exists(new_dir):
		return

	dirs = new_dir.split('/')
	new_dir = ''
	for f in dirs:
		new_dir += f+'/'
		create_dir_individual(new_dir, verbose=verbose)

###################################################################################################################################################

def save_pickle(filedir:str, file:object,
	verbose=VERBOSE,
	):
	'''
	Parameters
	----------
	filedir: filedir of file to save
	file: object to save. Be careful with cuda serialized objects
	'''
	assert isinstance(filedir, str)
	if verbose==1:
		prints.print_green(f'> saving: {filedir}')
	
	create_dir('/'.join(filedir.split('/')[:-1]), verbose=int(verbose==2))
	file_pi = open(filedir, 'wb')
	pickle.dump(file, file_pi)
	file_pi.close()
	
def load_pickle(filedir:str,
	return_none_if_missing=False,
	verbose=VERBOSE,
	):
	'''
	Parameters
	----------
	filedir: filedir of file to read

	Return
	----------
	file (object): the read object from disk
	'''
	if filedir is None:
		return None

	if not filedir_exists(filedir):
		if return_none_if_missing:
			return None
		else:
			raise Exception(f'no file in {filedir}')

	if verbose==1:
		prints.print_blue(f'> loading: {filedir}')

	pickle_in = open(filedir,'rb')
	file = pickle.load(pickle_in)
	pickle_in.close()
	return file

###################################################################################################################################################

def save_time_stamp(rootdir,
	extra_info={},
	cfilename='time_stamp',
	):
	create_dir(rootdir)
	filedir = f'{rootdir}/{cfilename}.txt'
	with open(filedir, 'w') as text_file:
		date, hour = get_date_hour()
		text_file.write(f'{date}\n')
		text_file.write(f'{hour}\n')
		if len(extra_info.keys())>0:
			text_file.write(f'\n')
			text_file.write(f'[extra_info]\n')
			for k in extra_info.keys():
				text_file.write(f'{k}={extra_info[k]}\n')

###################################################################################################################################################

def get_dict_from_filedir(filedir:str,
	key_key_separator:str=KEY_KEY_SEP_CHAR,
	key_value_separator:str=KEY_VALUE_SEP_CHAR,
	):
	splits = filedir.split('/')
	ret_dict = {
		FILEDIR:filedir,
		ROOTDIR:'/'.join(splits[:-1]),
		FILENAME:'.'.join(splits[-1].split('.')),
		CFILENAME:'.'.join(splits[-1].split('.')[:-1]),
		FEXT:splits[-1].split('.')[-1],
	}
	ret_dict.update(strings.get_dict_from_string(ret_dict[CFILENAME],
		key_key_separator,
		key_value_separator,
	))
	return ret_dict

def search_for_filedirs(rootdir:str,
	string_query:list=[''],
	string_filter:list=[],
	fext:str=None,
	verbose:int=VERBOSE,
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
		cfilename = filedict[CFILENAME]
		if strings.query_strings_in_string(string_query, cfilename) and not strings.query_strings_in_string(string_filter, cfilename):
			filedirs_res.append(filedir)

	prints.print_bar()
	print(f'filedirs after searching with filters: ({rootdir})')
	for k,filedir in enumerate(filedirs_res):
		filesize = get_filesize(filedir)
		print(f'({k}) - {filedir} - {filesize:.3f}[mbs]')
	prints.print_bar()
	return filedirs_res

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
			if fext is None or f.split('.')[-1]==fext: # dont add if none
				filedirs += [f'{root}/{f}']
	return filedirs

def get_roodirs(rootdir):
	depth = len(rootdir.split('/'))
	roodirs = []
	for root, dirs, files in os.walk(rootdir):
		sub_depth = len(root.split('/'))
		if sub_depth-depth==1:
			roodirs += [root]
	return roodirs

def get_nof_filedirs(filedir:str,
	fext:str=None,
	):
	'''
	return the count of filenames with an extention .fext
	'''
	return len(get_filedirs(filedir, fext=fext))

def print_all_filedirs(filedir):
	print(f'total files in {filedir}: {get_nof_filedirs(filedir)}')
	for root, dirs, files in os.walk(filedir):
		level = root.replace(filedir, '').count(os.sep)
		indent = ' ' * 4 * (level)+'> '
		print(f'{indent}{os.path.basename(root)}/')
		subindent = ' ' * 4 * (level + 1)+'- '
		for f in files:
			print(f'{subindent}{f}')

###################################################################################################################################################

def getmtime(filedir):
	return time.ctime(os.path.getmtime(filedir))

def getctime(filedir):
	return time.ctime(os.path.getmtime(filedir))

def get_newest_filedir(filedirs,
	mode='m',
	):
	if mode=='c':
		dates = [getctime(f) for f in filedirs]
	elif mode=='m':
		dates = [getmtime(f) for f in filedirs]
	else:
		raise Exception(f'{mode}')
	max_date = max(dates)
	filedir = filedirs[dates.index(max_date)]
	return filedir

###################################################################################################################################################

class PFile(object):
	def __init__(self, filedir,
		file=None,
		verbose=VERBOSE,
		):
		self.set_filedir(filedir)
		self.set_file(file)
		self.verbose = verbose
		self.reset()

	def set_filedir(self, filedir):
		self.is_dummy = filedir is None
		self.filedir = filedir

	def set_file(self, file):
		self.file = file

	def reset(self):
		if not self.is_dummy:
			self.filedict = get_dict_from_filedir(self.filedir)
			self.rootdir = self.filedict['_rootdir']
			self.filename = self.filedict['_filename']
			self.cfilename = self.filedict['_cfilename']
			self.fext = self.filedict['_fext']
			self.disk_size = get_filesize(self.filedir)
			self.last_state = 'idle'

			### attemp reading
			if self.file is None:
				if not self.disk_size is None: # file exists in disk
					self.load()
				else:
					raise Exception(f'no PFile.file and {self.filedir} does not exist in disk')
			else:
				pass
			return

	def __getitem__(self, idx):
		return self.filedict[idx]

	def __repr__(self):
		if not self.is_dummy:
			d = {
				'cfilename':self.cfilename,
				'fext':self.fext,
				'rootdir':self.rootdir,
				'file_class':type(self.file).__name__,
				'disk_size':f'{self.disk_size:.3f} [mb]' if not self.disk_size is None else None,
				'last_state':self.last_state,
				}
			txt = f'PFile({strings.get_string_from_dict(d, key_key_separator=", ")})'
		else:
			txt = f'PFile(dummy)'
		return txt

	def get_file(self):
		return self.file

	def __call__(self):
		return self.get_file()

	def save(self,
		copy_filedirs=[],
		):
		if not self.is_dummy:
			return self._save(
				copy_filedirs,
				)
		else:
			return

	def _save(self,
		copy_filedirs=[],
		):
		filedirs = [self.filedir]+copy_filedirs
		for filedir in filedirs:
			save_pickle(filedir, self.file)
		self.last_state = 'saved'
		return

	def load(self):
		if not self.is_dummy:
			return self._load()

	def _load(self):
		file = load_pickle(self.filedir)
		self.set_file(file)
		self.reset()
		self.last_state = 'loaded'
		return

###################################################################################################################################################

def gather_files(rootdir,
	fext:str=None,
	):
	filedirs = get_filedirs(rootdir, fext=fext)
	return [PFile(filedir) for filedir in filedirs]

def gather_files_by_id(rootdir,
	id_key='id',
	key_key_separator:str=KEY_KEY_SEP_CHAR,
	key_value_separator:str=KEY_VALUE_SEP_CHAR,
	fext:str=None,
	):
	if id_key is None:
		files = gather_files(rootdir,
			fext,
			)
		file_ids = [f.cfilename for f in files]
		return files, file_ids

	else:
		filedirs = get_filedirs(rootdir, fext=fext)
		files = []
		file_ids = []
		for filedir in filedirs:
			filedict = get_dict_from_filedir(filedir,
				key_key_separator,
				key_value_separator,
				)
			files += [PFile(filedir)]
			file_ids += [filedict[id_key]]
		return files, file_ids

def get_kfold_rootdirs_dict(rootdir,
	kf_str=KFOLF_CHAR,
	):
	'''
	{
	[kf_set][kf] = rootdir
	}
	'''
	rootdirs = get_roodirs(rootdir)
	kfold_rootdirs_dict = nested_dict()
	for rd in rootdirs:
		kf, kf_set = rd.split('/')[-1].split(kf_str)
		kfold_rootdirs_dict[kf_set][kf] = rd
	return kfold_rootdirs_dict.to_dict()

def gather_files_by_kfold(rootdir, _kf, kf_set,
	id_key=None,
	key_key_separator:str=KEY_KEY_SEP_CHAR,
	key_value_separator:str=KEY_VALUE_SEP_CHAR,
	fext:str=None,
	kf_str=KFOLF_CHAR,
	imbalanced_kf_mode=IMBALANCED_KF_MODE,
	random_state=RANDOM_STATE,
	kfs=None,
	returns_all_kf_files=False,
	):
	'''
	format must be .../kf@kf_set/files

	imbalanced_kf_mode is used just in case a k-fold iteration is missing and there is an imbalance on files (mostly for debuggin while results are still iterating)
	the normal case is when all k-fold has the same amount of files!
	'''
	kfold_rootdirs_dict = get_kfold_rootdirs_dict(rootdir,
		kf_str=kf_str,
	)
	kf = str(_kf)
	if kf=='.': # gather files from all kf values
		all_kf_files = {}
		all_kf_file_ids = {}
		kfs = list(kfold_rootdirs_dict[kf_set].keys()) if kfs is None else kfs
		for _kf in kfs:
			kfrd = kfold_rootdirs_dict[kf_set][_kf]
			_files, _file_ids = gather_files_by_id(kfrd,
				id_key,
				key_key_separator,
				key_value_separator,
				fext,
				)
			assert len(_files)>0, f'no files for kf={_kf}'
			all_kf_files[_kf] = _files
			all_kf_file_ids[_kf] = [f'{_kf}{kf_str}{_fid}' for _fid in _file_ids]

		# print(all_kf_files); print(all_kf_file_ids)
		max_len = max([len(all_kf_files[_kf]) for _kf in kfs])
		if imbalanced_kf_mode=='ignore':
			pass

		elif imbalanced_kf_mode=='error':
			for _kf in kfs:
				assert len(all_kf_files[_kf])==max_len, f'not equal size of kf files in all kf values {[len(all_kf_files[_kf]) for _kf in kfs]}'

		elif imbalanced_kf_mode=='oversampling':
			for _kf in kfs:
				_len = len(all_kf_files[_kf])
				k_repeat = max_len-_len
				if k_repeat>0:
					idxs = list(range(0, _len))
					new_idxs = lists.get_bootstrap(idxs, k_repeat,
						random_state=random_state,
						)
					all_kf_files[_kf] += [all_kf_files[_kf][idx] for idx in new_idxs]
					all_kf_file_ids[_kf] += [all_kf_file_ids[_kf][idx] for idx in new_idxs]
		else:
			raise Exception(f'imbalanced_kf_mode={imbalanced_kf_mode}')

		# print(all_kf_files); print(all_kf_file_ids)
		files = []
		file_ids = []
		for _kf in kfs:
			files += all_kf_files[_kf]
			file_ids += all_kf_file_ids[_kf]

		if returns_all_kf_files:
			return files, file_ids, kfs, all_kf_files
		else:
			return files, file_ids, kfs

	else: # gather files from an specific kf value
		if not kf_set in kfold_rootdirs_dict.keys():
			return [], [], []
		kfold_rootdirs_dict_set = kfold_rootdirs_dict[kf_set]
		if not kf in kfold_rootdirs_dict_set.keys():
			return [], [], []
		kfrd = kfold_rootdirs_dict_set[str(kf)]
		files, file_ids = gather_files_by_id(kfrd,
			id_key,
			key_key_separator,
			key_value_separator,
			fext,
			)
		return files, file_ids, [kf]