import os
import json
import math
import errno
import shutil
import glob
import platform

def mkdir_p(path):
	try:
		os.makedirs(path)
	except OSError as exc:
		import errno
		if exc.errno == errno.EEXIST and os.path.isdir(path):
			pass
		else:
			raise

def format_chapter_time(input_seconds):
	hours = math.floor(input_seconds / 3600)
	minutes = math.floor(input_seconds % 3600 / 60)
	seconds = math.floor(input_seconds % 3600 % 60)
	milliseconds = int(math.modf(input_seconds)[0] * 1000)
	return f'{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}'

def get_bookmark_data(file_path):
	print("Opening bookmarks file:", file_path)
	try:
		with open(file_path, "rb") as f:
			try:
				data = json.load(f)
				return data
			except:
				print("JSON parsing failed.")
	except:
		print("Error reading file...")
		pass
		
	return False
	
bookmarks_file = os.getenv('APPDATA') + "/mpv/bookmarks.json"

data = get_bookmark_data(bookmarks_file)
if data == False:
	marks = glob.glob("bookmarks/*.json")
	if len(marks) > 0:
		data = get_bookmark_data(marks[-1])

if data == False:
	print("No bookmark data. Aborting...")
	exit()

filename = ''
chapters = []
for k, timestamp in sorted(data.items()):
	if filename != '' and filename != timestamp['filename']:
		print("CONFLICTING FILE NAMES:")
		print(f"  {filename}   <>   {timestamp['filename']}")
		print("ABORTING....")
		exit()
		
	filename = timestamp['filename']
	info = format_chapter_time(timestamp['pos'])
	chapters.append(info)

if chapters[0] != '00:00:00.000':
	chapters.insert(0, '00:00:00.000')
	
filename, ext = os.path.splitext(filename)
output_file = f'{filename}.chapters.txt'

chapters_formatted = []
for index, timestamp in enumerate(chapters):
	chapter_time = f'CHAPTER{index+1:02d}={timestamp}'
	chapters_formatted.append(chapter_time)
	
	chapter_label = f'CHAPTER{index+1:02d}NAME='
	chapters_formatted.append(chapter_label)

print(f"Writing {len(chapters)} chapters to {output_file}...")

with open(output_file, "wb") as f:
	f.write('\n'.join(chapters_formatted).encode('utf-8'))

if platform.system() == 'Windows':
	os.startfile(output_file)

if os.path.exists(bookmarks_file):
	mkdir_p("bookmarks")
	shutil.move(bookmarks_file, f"bookmarks/{filename}.json")
