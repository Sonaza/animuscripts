import os
import glob
import math
import AssParser
import re

def mkdir_p(path):
	try:
		os.makedirs(path)
	except OSError as exc:
		import errno
		if exc.errno == errno.EEXIST and os.path.isdir(path):
			pass
		else:
			raise

def rgb_luminance(r, g, b, a):
    luminanceR = 0.22248840
    luminanceG = 0.71690369
    luminanceB = 0.06060791
    return ((r / 255) * luminanceR) + ((g / 255) * luminanceG) + ((b / 255) * luminanceB)
	
def adjust_brightness(multiplier, r, g, b, a):
	r = min(255, int(r * multiplier))
	g = min(255, int(g * multiplier))
	b = min(255, int(b * multiplier))
	return (r, g, b, a)

output_folder = ''
if output_folder:
	mkdir_p(output_folder)

subs_files = glob.glob("subtitles/*.ass")
video_files = glob.glob("*.mkv")

if len(video_files) < len(subs_files):
	video_files = [''] * len(subs_files)
video_subs_map = list(zip(video_files, subs_files))

def scaleDialogue(dialogue_text, multiplier):
	operations = [
		# Font size
		[
			r'(?<=\\fs)([0-9]+)',
			lambda m: str(math.floor(int(m.group(1)) * multiplier))
		],
		# Border
		[
			r'(?<=\\bord)([.0-9]+)',
			lambda m: f"{float(m.group(1)) * multiplier:g}"
		],
		# Position
		[
			r'(?<=\\pos\()([.0-9]+),([.0-9]+)(?=\))',
			lambda m: f"{float(m.group(1)) * multiplier:g},{float(m.group(2)) * multiplier:g}"
		],
		# Origin
		[
			r'(?<=\\org\()([.0-9]+),([.0-9]+)(?=\))',
			lambda m: f"{float(m.group(1)) * multiplier:g},{float(m.group(2)) * multiplier:g}"
		],
		# Move with 4 parameters
		[
			r'(?<=\\move\()([.0-9]+),([.0-9]+),([.0-9]+),([.0-9]+)(?=\))',
			lambda m: f"{float(m.group(1)) * multiplier:g},{float(m.group(2)) * multiplier:g},{float(m.group(3)) * multiplier:g},{float(m.group(4)) * multiplier:g}"
		],
		# Move with 6 parameters
		[
			r'(?<=\\move\()([.0-9]+),([.0-9]+),([.0-9]+),([.0-9]+),([.0-9]+),([.0-9]+)(?=\))',
			lambda m: f"{float(m.group(1)) * multiplier:g},{float(m.group(2)) * multiplier:g},{float(m.group(3)) * multiplier:g},{float(m.group(4)) * multiplier:g},{m.group(5)},{m.group(6)}"
		],
		# Clip
		[
			r'(?<=\\clip\()([.0-9]+),([.0-9]+),([.0-9]+),([.0-9]+)(?=\))',
			lambda m: f"{float(m.group(1)) * multiplier:g},{float(m.group(2)) * multiplier:g},{float(m.group(3)) * multiplier:g},{float(m.group(4)) * multiplier:g}"
		],
		# Inverted Clip
		[
			r'(?<=\\iclip\()([.0-9]+),([.0-9]+),([.0-9]+),([.0-9]+)(?=\))',
			lambda m: f"{float(m.group(1)) * multiplier:g},{float(m.group(2)) * multiplier:g},{float(m.group(3)) * multiplier:g},{float(m.group(4)) * multiplier:g}"
		],
	]
	
	for pattern, repl_lambda in operations:
		dialogue_text = re.sub(pattern, repl_lambda, dialogue_text)
	
	return dialogue_text

def match_any_substr(needles, haystack):
	return any(x.lower() in haystack.lower() for x in needles)

for input_video, input_subtitle in video_subs_map:
	try:
		data = AssParser.parse_file(input_subtitle)
	except AssParser.AssParseError as e:
		print(f"Failed to parse file: {e}")
		break
		
	subtitle_output_file = os.path.basename(input_subtitle)
	if len(input_video) > 0:
		video_filename, ext = os.path.splitext(input_video)
		subtitle_output_file = f"{video_filename}.ass"
		
	originalPlayRes = [data['Script Info']['PlayResX'], data['Script Info']['PlayResY']]
	
	# data['Script Info']['PlayResX'] = 1920
	# playResMultiplier = math.floor(data['Script Info']['PlayResX'] / originalPlayRes[0])
	# data['Script Info']['PlayResY'] = int(playResMultiplier * originalPlayRes[1])
	
	try:
		if data['V4+ Styles']['Style'][0]['Name'] == 'Default':
			del data['V4+ Styles']['Style'][0]
	except: pass
	
	for fields in data['V4+ Styles']['Style']:
		# fields['Fontname'] = 'Gandhi Sans'
		
		
		# fields['Fontsize'] = fields['Fontsize'] * playResMultiplier
		# fields['MarginV'] = int(fields['MarginV'] * max(1, playResMultiplier * 0.67))
		# fields['MarginL'] = int(fields['MarginL'] * playResMultiplier)
		# fields['MarginR'] = int(fields['MarginR'] * playResMultiplier)
		
		# fields['Shadow'] = math.floor(fields['Shadow'] * playResMultiplier)
		# fields['Outline'] = math.floor(fields['Outline'] * max(1, playResMultiplier * 0.67))
		
		# if match_any_substr(['main', 'italics', 'flashback'], fields['Name']):
		if match_any_substr(['Rosario'], fields['Fontname']):
			fields['Bold'] = 1
		# 	fields['Shadow'] = 2
		# 	fields['Outline'] = 4
			
		# 	fields['PrimaryColour'] = AssParser.format_hex_color('ffffff')
			
		# 	if sum(fields['OutlineColour']) == 0:
		# 		fields['OutlineColour'] = AssParser.format_hex_color('3e4703')

		# 	fields['BackColour']    = AssParser.format_hex_color('2e2706', 90)
		
		# if match_any_substr(['Ep_Title'])
		
	for fields in data['Events']['Dialogue']:
		# fields['Text'] = scaleDialogue(fields['Text'], playResMultiplier)
		
		# if 'Main' in fields['Name'] or 'Italics' in fields['Name'] or 'Flashback' in fields['Name']:
		# 	fields['Shadow'] = 2
		# 	fields['Outline'] = 2
			
		# 	if 'Flashback' in fields['Name']:
		# 		fields['PrimaryColour'] = format_hex_color('edf2f8')
		# 		fields['OutlineColour'] = format_hex_color('595a71')
		# 		fields['BackColour']    = format_hex_color('25263a', 90)
				
		# else:
		# 	colorRGBA = fields['PrimaryColour']
		# 	luminance = rgb_luminance(*colorRGBA)
		# 	primaryColor = colorRGBA
		# 	outlineColor = colorRGBA
			
		# 	if luminance < 0.4:
		# 		primaryColor = parse_style_color('&H00F3F6F8')
		# 	else:
		# 		primaryColor = adjust_brightness(3.0, *primaryColor)
				
		# 	if luminance > 0.6:
		# 		outlineColor = adjust_brightness(0.3, *outlineColor)
		# 	elif luminance > 0.35:
		# 		outlineColor = adjust_brightness(0.6, *outlineColor)
			
		# 	fields['PrimaryColour'] = format_style_color(*primaryColor)
		# 	fields['OutlineColour'] = format_style_color(*outlineColor)
		# 	fields['BackColour'] = format_style_color(*outlineColor, 150)
			
		# 	fields['Fontsize'] = max(10, int(fields['Fontsize']))
			
		# 	fields['Shadow'] = 1
		# 	fields['Outline'] = 1
		pass
		
	
	output_filename = os.path.join(output_folder, subtitle_output_file)
	try:
		AssParser.save_file(data, output_filename)
		print(f"Saved '{output_filename}'")
	except AssParser.AssFormatError as e:
		print("Formatting error: " + e)
		break
	
	# break
