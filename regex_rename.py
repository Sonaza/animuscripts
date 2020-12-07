import os
import glob
import re

files = []
glob_strings = ["*.mkv", "*.ass"]
for glob_str in glob_strings:
	files.extend(glob.glob(glob_str))

pattern = re.compile(r'(\[\w{1,8}\])')
# pattern = re.compile(r'([\[\(].*?[\]\)])')

for file in files:
	# newname = file
	newname, ext = os.path.splitext(file)
	
	newname = pattern.sub('', newname)
	newname = newname.replace("", "")
	newname = newname.replace("", "")
	newname = newname.replace("", "")
	
	newname = f'{newname.strip()}{ext}'
	
	print(file, "=>", newname)
	if (file != newname): os.rename(file, newname)
