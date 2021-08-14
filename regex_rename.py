import os
import glob
import re

def convertToAscii(inputString, replace=" "):
	output = ""
	for c in inputString:
		if ord(c) < 128:
			output += c
		else:
			output += replace
	
	return output
	
def scan(base_path):
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
	

files, folders = scan('.')
files = sorted(files)

pattern = re.compile(r'(\[\w{1,8}\])')
pattern = re.compile(r'([\[\(].*?[\]\)])')

for file in files:
	newname, ext = os.path.splitext(file)
	
	newname = pattern.sub('', newname)
	
	newname = newname.replace("", "")
	newname = newname.replace("", "")
	newname = newname.replace("", "")
	
	newname = f'{newname.strip()}{ext}'
	
	print(f'  {(file).ljust(100)}  =>  {newname}')
	# if (file != newname): os.rename(file, newname)
