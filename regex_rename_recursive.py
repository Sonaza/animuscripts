import os
import glob
import re

def scan_recursively(base_path):
	allowed_ext = ['.mkv', '.mp4', '.ass']
	result_files = []
	result_folders = []
	for root, subfolders, files in os.walk(base_path):
		for subfolder in subfolders:
			result_folders.append(os.path.relpath(os.path.join(root, subfolder), base_path))
		
		for file in files:
			newname, ext = os.path.splitext(file)
			if not ext in allowed_ext:
				continue
			
			result_files.append(os.path.relpath(os.path.join(root, file), base_path))
	
	return (result_files, result_folders)

files, folders = scan_recursively('.')
# Append folders in reverse order at the end (prevent file not found errors when folders are renamed before files)
files.extend(list(reversed(folders))) 

bracket_pattern = re.compile(r'([\[\(].*?[\]\)])')
space_pattern   = re.compile(r'( {2,})')

current_root = '.'

for original_file in files:	
	root, file = os.path.split(original_file)
	
	if current_root != root:
		print(f"Current folder: {root}\\")
		current_root = root
	
	newname, ext = os.path.splitext(file)
	
	newname = bracket_pattern.sub('', newname)
	newname = space_pattern.sub(' ', newname)
	
	newname = newname.replace("", "")
	newname = newname.replace("", "")
	newname = newname.replace("", "")
	
	newname = f'{newname.strip()}{ext}'
	
	if (file == newname):
		continue
	
	dir_flag = '\\ (dir)' if os.path.isdir(original_file) else ''
	
	if len(newname) == 0:
		print(f'  {(file + dir_flag).ljust(100)}  =>  (invalid filename!)')
		print( '    ERROR: Name renaming has made the path completely empty. Skipping...')
		continue
	
	# if file != newname and os.path.exists(os.path.join(root, newname)):
	# 	print(f'  {(file + dir_flag).ljust(100)}  =>  {newname.ljust(60)}')
	# 	continue
	
	print(f'  {(file + dir_flag).ljust(100)}  =>  {newname}')
	
	try:
		if (file != newname): os.rename(original_file, os.path.join(root, newname))
		pass
		
	except FileExistsError as e:
		print("    ERROR: Target path already exists!")
		
	except Exception as e:
		print("    ERROR:", e)
