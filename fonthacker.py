import os
import glob

def mkdir_p(path):
	try:
		os.makedirs(path)
	except OSError as exc:
		import errno
		if exc.errno == errno.EEXIST and os.path.isdir(path):
			pass
		else:
			raise

class FieldsParseError(Exception):
	pass

class InvalidFields(Exception):
	pass
	
class ColorValueError(Exception):
	pass

def load_file(filename, mode = "rb"):
	with open(filename, mode) as f:
		data = f.readlines()
		data = [x.decode('utf-8').strip() for x in data]
		return data
	
	return False

def save_file(filename, data):
	with open(filename, 'wb') as f:
		f.write(data.encode('utf-8'))

field_names = [
	'Name',
	'Fontname',
	'Fontsize',
	'PrimaryColour',
	'SecondaryColour',
	'OutlineColour',
	'BackColour',
	'Bold',
	'Italic',
	'Underline',
	'StrikeOut',
	'ScaleX',
	'ScaleY',
	'Spacing',
	'Angle',
	'BorderStyle',
	'Outline',
	'Shadow',
	'Alignment',
	'MarginL',
	'MarginR',
	'MarginV',
	'Encoding',
]

def parse_style_line(style_line):
	if not ('Style:' in style_line[0:6]):
		raise FieldsParseError()
	
	values = style_line[6:].strip().split(',')
	if len(values) != 23:
		print(f"Number of fields is not correct: expected 23, found {len(values)}")
		raise FieldsParseError()
		
	fields = dict(zip(field_names, values))
	return fields

def reformat_style_line(style_fields):
	if not isinstance(style_fields, dict):
		raise InvalidFields()
		
	if not all(field in style_fields for field in field_names):
		raise InvalidFields()
	
	values = [str(style_fields[field]) for field in field_names]
	return f"Style: {','.join(values)}"

def rgb_luminance(r, g, b, a):
    luminanceR = 0.22248840
    luminanceG = 0.71690369
    luminanceB = 0.06060791
    return ((r / 255) * luminanceR) + ((g / 255) * luminanceG) + ((b / 255) * luminanceB)

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
	
def format_style_color(r, g, b, a):
	return f'&H{a:02X}{b:02X}{g:02X}{r:02X}'
	
def adjust_brightness(multiplier, r, g, b, a):
	r = min(255, int(r * multiplier))
	g = min(255, int(g * multiplier))
	b = min(255, int(b * multiplier))
	return (r, g, b, a)

output_folder = ''
if output_folder:
	mkdir_p(output_folder)

subs_files = glob.glob("subs/*.ass")

for input_file in subs_files:
	subs_data = load_file(input_file)
	if subs_data == False:
		print(f"Load error: {input_file}")
		break
		
	output_data = []

	for line in subs_data:
		try:
			fields = parse_style_line(line)
		except FieldsParseError:
			# Not style line, append as is
			output_data.append(line)
			continue
		
		if 'Love Asteroid' in fields['Name']:
			fields['Shadow'] = 2
			fields['Outline'] = 2
			
			fields['OutlineColour'] = '&H00922915'
			fields['BackColour']    = '&H55922915'
		else:
			colorRGBA = parse_style_color(fields['PrimaryColour'])
			luminance = rgb_luminance(*colorRGBA)
			primaryColor = colorRGBA
			outlineColor = colorRGBA
			
			if luminance < 0.4:
				primaryColor = parse_style_color('&H00F3F6F8')
			else:
				primaryColor = adjust_brightness(3.0, *primaryColor)
				
			if luminance > 0.6:
				outlineColor = adjust_brightness(0.3, *outlineColor)
			elif luminance > 0.35:
				outlineColor = adjust_brightness(0.6, *outlineColor)
			
			fields['PrimaryColour'] = format_style_color(*primaryColor)
			fields['OutlineColour'] = format_style_color(*outlineColor)
			
			fields['Shadow'] = 1
			fields['Outline'] = 2 #2 if int(fields['Outline']) > 1 else 0
		
		try:
			formatted = reformat_style_line(fields)
		except InvalidFields:
			print("Failed to format fields back to string.")
			continue
		
		output_data.append(formatted)
	
	output_filename = os.path.join(output_folder, os.path.basename(input_file))
	print(f"Saved '{output_filename}'")
	
	save_file(output_filename, '\n'.join(output_data))
	
	# break
