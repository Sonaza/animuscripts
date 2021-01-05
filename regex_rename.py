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

files = []
glob_strings = ["*.mkv", "*.ass"]
for glob_str in glob_strings:
	files.extend(glob.glob(glob_str))

files.extend([x for x in os.listdir('.') if os.path.isdir(x)])

pattern = re.compile(r'(\[\w{1,8}\])')
pattern = re.compile(r'([\[\(].*?[\]\)])')

for file in files:
	# newname = file
	if not os.path.isdir(file):
		newname, ext = os.path.splitext(file)
	else:
		newname = file
		ext = ''
	
	newname = pattern.sub('', newname)
	
	newname = newname.replace("", "")
	newname = newname.replace("", "")
	newname = newname.replace("", "")
	
	newname = f'{newname.strip()}{ext}'
	
	print(f'  {(file).ljust(100)}  =>  {newname}')
	# if (file != newname): os.rename(file, newname)
