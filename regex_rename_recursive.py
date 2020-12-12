import os
import glob
import re

def scan_recursively(base_path, include_folders):
	allowed_ext = ['.mkv', '.mp4', '.ass']
	result = []
	for root, subfolders, files in os.walk(base_path):
		if include_folders:
			for subfolder in subfolders:
				result.append(os.path.relpath(os.path.join(root, subfolder), base_path))
		
		for file in files:
			newname, ext = os.path.splitext(file)
			if not ext in allowed_ext:
				continue
			
			result.append(os.path.relpath(os.path.join(root, file), base_path))
	
	return result

files = scan_recursively('.', True)

# pattern = re.compile(r'(\[\w{1,8}\])')
bracket_pattern = re.compile(r'([\[\(].*?[\]\)])')
space_pattern   = re.compile(r'( {2,})')

current_root = '.'

for original_file in files:	
	root, file = os.path.split(original_file)
	
	if current_root != root:
		print(f"Current folder: {root}/")
		current_root = root
	
	newname, ext = os.path.splitext(file)
	
	newname = bracket_pattern.sub('', newname)
	newname = space_pattern.sub(' ', newname)
	
	newname = newname.replace("", "")
	newname = newname.replace("", "")
	newname = newname.replace("", "")
	
	newname = f'{newname.strip()}{ext}'
	
	dir_flag = '/ (dir)' if os.path.isdir(original_file) else ''
	
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
