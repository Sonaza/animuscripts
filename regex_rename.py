import os
import glob
import re

files = []
glob_strings = ["*.mkv", "*.ass"]
for glob_str in glob_strings:
	files.extend(glob.glob(glob_str))

files.extend([x for x in os.listdir('.') if os.path.isdir(x)])

pattern = re.compile(r'(\[\w{1,8}\])')
pattern = re.compile(r'([\[\(].*?[\]\)])')

for file in files:
	# newname = file
	newname, ext = os.path.splitext(file)
	
	newname = pattern.sub('', newname)
	newname = f'{newname.strip()}{ext}'
	newname = newname.replace("", "")
	newname = newname.replace("", "")
	newname = newname.replace("", "")
	
	
	print(file, "=>", newname)
	if (file != newname): os.rename(file, newname)
