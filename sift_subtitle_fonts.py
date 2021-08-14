import os
import glob
import shutil
import re
from fontTools import ttLib

class ParseError(Exception):
	pass

def load_file(filename, mode = "rb"):
	with open(filename, mode) as f:
		data = f.readlines()
		data = [x.decode('utf-8').strip() for x in data]
		return data
	return False
	
FONT_SPECIFIER_NAME_ID = 4
FONT_SPECIFIER_FAMILY_ID = 1
def get_font_name(font_path):
	font = ttLib.TTFont(font_path)
	name = ""
	family = ""
	for record in font['name'].names:
		try:
			if b'\x00' in record.string:
				name_str = record.string.decode('utf-16-be')
			else:
				name_str = record.string.decode('utf-8')
		except UnicodeError:
			continue
			
		if record.nameID == FONT_SPECIFIER_NAME_ID and not name:
			name = name_str
			
		elif record.nameID == FONT_SPECIFIER_FAMILY_ID and not family: 
			family = name_str
			
		if name and family:
			break
			
	return name, family
	
subtitles_folder = "subtitles"
fonts_folder = "attachments"

subtitles_files = glob.glob(os.path.join(subtitles_folder, "*.ass"))
subtitles_files = list(filter(lambda x: 'dialog' in x, subtitles_files))

used_fonts_folder = "used_attachments"
if not os.path.exists(used_fonts_folder):
	os.mkdir(used_fonts_folder)

def scan_folder(folder_path, allowed_extensions):
	allowed_extensions = [x.lower() for x in allowed_extensions]
	result = []
	for root, subdirs, files in os.walk(fonts_folder):
		for filename in files:
			_, ext = os.path.splitext(filename)
			if ext.lower()[1:] in allowed_extensions:
				result.append(os.path.join(root, filename))
	return result
	
def scan_fonts(fonts_folder):
	font_names = {}
	fonts_files = scan_folder(fonts_folder, ['otf', 'ttf'])
	for font_file in fonts_files:
		font_name, font_family = get_font_name(font_file)
		identifier = font_family.lower()
		if not identifier in font_names:
			font_names[identifier] = {'name': font_name, 'family': font_family, 'file': font_file}
	return font_names
	
font_names = scan_fonts(fonts_folder)

def find_font(font_name):
	font_name = font_name.lower()
	for identifier, font_info in font_names.items():
		if identifier in font_name:
			return font_info
	return False

field_names = [
	'Name', 'Fontname', 'Fontsize',
	'PrimaryColour', 'SecondaryColour', 'OutlineColour', 'BackColour',
	'Bold', 'Italic', 'Underline', 'StrikeOut',
	'ScaleX', 'ScaleY', 'Spacing', 'Angle',
	'BorderStyle', 'Outline', 'Shadow',
	'Alignment', 'MarginL', 'MarginR', 'MarginV',
	'Encoding',
]

def parse_style_line(style_line):
	if not ('Style:' in style_line[0:6]):
		raise ParseError()
	
	values = style_line[6:].strip().split(',')
	if len(values) != 23:
		print(f"Number of fields is not correct: expected 23, found {len(values)}")
		raise ParseError()
		
	fields = dict(zip(field_names, values))
	return fields

def parse_dialogue_line(dialogue_line):
	if not ('Dialogue:' in dialogue_line[0:9]):
		raise ParseError()
	
	fn_pattern = re.compile(r'(?:\\fn)([^\\]+?)(?:\\|\})')
	m = fn_pattern.search(dialogue_line)
	try:
		return m.group(1)
	except:
		raise ParseError()

for file_name in subtitles_files:
	subs_data = load_file(file_name)
	if subs_data == False:
		continue
	
	used_fonts = set()
	for line in subs_data:
		try:
			fields = parse_style_line(line)
			used_fonts.add(fields['Fontname'])
		except ParseError:
			pass
		
		try:
			font_name = parse_dialogue_line(line)
			used_fonts.add(font_name)
		except ParseError:
			pass	
	
	print(f"Fonts used in {file_name}:")
	for font_name in used_fonts:
		print(f"\t{font_name}")
		font_info = find_font(font_name)
		if font_info:
			print("\t\t", font_info)
			
			font_file = os.path.basename(font_info['file'])
			target_path = os.path.join(used_fonts_folder, font_file)
			if not os.path.exists(target_path):
				shutil.copyfile(font_info['file'], target_path)
		
	print()
	
	# break
