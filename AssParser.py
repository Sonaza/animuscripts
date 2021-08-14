import os

class ColorValueError(Exception):  pass
class AssParseError(Exception):  pass
class AssFormatError(Exception): pass

def _load_file(filename, mode = "rb"):
	with open(filename, mode) as f:
		data = f.readlines()
		data = [x.decode('utf-8-sig').strip() for x in data]
		return data
	return False

def parse_style_color(hex_color):
	if not isinstance(hex_color, str):
		raise ColorValueError()
	if len(hex_color) != 10:
		raise ColorValueError()
	if hex_color[0:2] != '&H':
		raise ColorValueError()
	
	# &HAABBGGRR
	a = int(hex_color[2:4], 16)
	b = int(hex_color[4:6], 16)
	g = int(hex_color[6:8], 16)
	r = int(hex_color[8:10], 16)
	return (r, g, b, a)
	
def format_hex_color(hex, alpha = 0):
	return f'&H{alpha:02X}{hex[4:6]}{hex[2:4]}{hex[0:2]}'.upper()
	
def format_style_color(r, g, b, a, alphaoverride = None):
	if alphaoverride != None: a = alphaoverride
	return f'&H{a:02X}{b:02X}{g:02X}{r:02X}'

def _try_parse(value):
	try: return parse_style_color(value)
	except: pass
	
	try: return int(value)
	except: pass
	
	try: return float(value)
	except: pass
	
	return value

def reformat_color_values(data, fields):
	for field in fields:
		if field in data and (len(data[field]) == 3 or len(data[field]) == 4):
			data[field] = format_style_color(*data[field])

def parse_file(file_path):
	if not os.path.exists(file_path):
		raise AssParseError(f"Target ASS file does not exist: {file_path}")
		
	file_data_lines = _load_file(file_path)
	
	if file_data_lines == False or len(file_data_lines) <= 1:
		raise AssParseError(f"Reading target ASS file failed or it is empty: {file_path}")
	
	data = {}
	ignore_line_characters = [';']
	
	current_section = None
	current_format = None
	
	for line in file_data_lines:
		if len(line) == 0 or line[0] in ignore_line_characters:
			continue
		
		if line[0] == '[' and line[-1] == ']':
			current_section = line[1:-1]
			if len(current_section) == 0:
				raise AssParseError("Section name is empty.")
			
			current_format = None
			
			if current_section != 'Aegisub Extradata':
				data[current_section] = {}
				
			continue
			
		elif line[0] == '[':
			raise AssParseError("Unexpected section label opening bracket without closing bracket")
		
		if current_section == None:
			raise AssParseError("No section label found before data")
			
		elif current_section == 'Aegisub Extradata':
			continue
		
		key, value = line.split(':', 1)
		value = value.strip()
		
		if key == 'Format':
			current_format = [x.strip() for x in value.split(',')]
			continue
		
		if key == 'Style' or key == 'Dialogue':
			if current_format == None:
				raise AssParseError("Format fields are not declared")
			
			if key not in data[current_section]:
				data[current_section][key] = []
			
			formatted_values = [_try_parse(x) for x in value.split(',', len(current_format) - 1)]
			
			value_dict = dict(zip(current_format, formatted_values))
			data[current_section][key].append(value_dict)
		
		elif key == "Comment":
			## NAADA
			continue
		
		else:
			if key in data[current_section]:
				raise AssParseError(f"Unexpected duplicate field in section. Section: {current_section}  Key: {key}")
				
			data[current_section][key] = _try_parse(value)
	
	if 'Script Info' not in data:
		raise AssParseError("Missing 'Script Info' section")
	if 'V4+ Styles' not in data:
		raise AssParseError("Missing 'V4+ Styles' section")
	if 'Events' not in data:
		raise AssParseError("Missing 'Events' section")
		
	# import json
	# print(json.dumps(data, indent=2))
	return data

def format_file(ass_data):
	output_formatted = []
	
	if 'Script Info' not in ass_data:
		raise AssFormatError("Missing 'Script Info' section")
	if 'V4+ Styles' not in ass_data:
		raise AssFormatError("Missing 'V4+ Styles' section")
	if 'Events' not in ass_data:
		raise AssFormatError("Missing 'Events' section")
	
	style_format = None
	dialogue_format = None
	
	for section_name, section_data in ass_data.items():
		output_formatted.append(f'[{section_name}]')
		if section_name == 'Script Info':
			output_formatted.append(f'; Script reformatted by the font hacker script')
			output_formatted.append(f'; Cool beans and stuff')
		
		for key, values in section_data.items():
			if key == 'Style' and style_format == None:
				if len(values) == 0: raise AssFormatError(f"Section '{section_name}' has no values")
				style_format = list(values[0].keys())
				output_formatted.append(f"Format: {', '.join(style_format)}")
				
			if key == 'Dialogue' and dialogue_format == None:
				if len(values) == 0: raise AssFormatError(f"Section '{section_name}' has no values")
				dialogue_format = list(values[0].keys())
				output_formatted.append(f"Format: {', '.join(dialogue_format)}")
				output_formatted.append('')
			
			if key == 'Style' or key == 'Dialogue':
				for row in list(values):
					reformat_color_values(row, ['PrimaryColour', 'SecondaryColour', 'OutlineColour', 'BackColour'])
					output_formatted.append(f"{key}: {','.join([str(y) for x, y in row.items()])}")
			else:
				output_formatted.append(f"{key}: {str(values)}")
		
		output_formatted.append('')
	
	return output_formatted
		
def save_file(ass_data, output_file):
	try:
		formatted_data = format_file(ass_data)
	except AssFormatError as e:
		print(e)
		return False
	
	with open(output_file, "wb") as f:
		for line in formatted_data:
			f.write(line.encode('utf-8') + b'\r\n')
	
	return True
