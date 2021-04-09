import os
import glob
import subprocess
import json
import re

def pp(program_name): return os.path.join('F:\\Animu\\_Tools', program_name)
mkvmerge   = pp('mkvmerge')

video_files = glob.glob("*.mkv")

text_codecs = {
	"S_TEXT/SSA": ".ssa",
	"S_TEXT/ASS": ".ass",
	"S_TEXT/UTF8": ".srt",
	"S_TEXT/ASCII": ".srt",
}

subs_output_folder = "subtitles"
attachments_output_folder = "attachments"

def match_any_exact(needles, haystack):
	for index, needle in enumerate(needles):
		if needle.lower() == haystack.lower():
			return index + 1
	return -1
	# return any(x.lower() == haystack.lower() for x in needles)

def match_any_substr(needles, haystack):
	for index, needle in enumerate(needles):
		if needle.lower() in haystack.lower():
			return index
	return -1
	# return any(x.lower() in haystack.lower() for x in needles)

def get_file_tracks(file_path):
	if not os.path.exists(file_path):
		print("File does not exist:", file_path)
		return ([], [])
	
	command = [mkvmerge, '-i', '-F', 'json', file_path]
	output = subprocess.check_output(command, stderr=subprocess.STDOUT).decode("utf-8")
	
	try:
		data = json.loads(output)
	except json.JSONDecodeError as e:
		print("Failed to parse mkvmerge output:", e)
		return ([], [])
	
	tracks = {
		"audio"     : [],
		"subtitles" : [],
	}
	for track_info in data['tracks']:
		track_type = track_info['type']
		if not track_type in ['audio', 'subtitles']:
			continue
		
		try:
			track_name = track_info['properties']['track_name']
		except:
			track_name = ''
		
		info = {
			"id":         track_info['id'],
			"codec_id":   track_info['properties']['codec_id'],
			"track_name": track_name,
			"language":   track_info['properties']["language"]
		}
		tracks[track_type].append(info)
	
	return tracks

class Match:
	ANY    = 0
	EXACT  = 1
	SUBSTR = 2

class Select:
	ALL         = 0
	FIRST_MATCH = 1

PRINT_TRACK_INFO = False

requirements = {
	"audio" : {
		"lang"        : ['jpn'],
		"lang_match"  : Match.EXACT,
		
		"name"        : [''],
		"name_match"  : Match.ANY,
		
		"select"      : Select.FIRST_MATCH,
	},
	
	"subtitles" : {
		"lang"        : ['eng'],
		"lang_match"  : Match.EXACT,
		
		"name"        : [('Dialogue', 4), ('English', 2)],
		"name_match"  : Match.EXACT,
		
		"select"      : Select.FIRST_MATCH,
	},
}

def match_track(track_data, search_key, method, needles_and_ids):
	track_id = track_data['id']
	haystack = track_data[search_key]
	
	needles = []
	track_ids = []
	for needle in needles_and_ids:
		if isinstance(needle, tuple):
			if len(needle) != 2:
				raise Exception("Expected language tuple to be (language, track_id)")
				
			needles.append(needle[0])
			track_ids.append(needle[1])
			
		elif isinstance(needle, str):
			needles.append(needle)
			track_ids.append(None);
	
	index = -1
	if method == Match.SUBSTR:
		index = match_any_substr(needles, haystack)
		
	elif method == Match.EXACT:
		index = match_any_exact(needles, haystack)
		
	elif method == Match.ANY:
		index = 0
	
	else:
		raise Exception("Not a supported match method")
	
	if index > 0 and track_ids[index-1] != None:
		if track_ids[index-1] != track_id:
			return -1
		
	return index
	

track_matches = {}

try:
	for input_file in video_files:
		print("Processing info from file", input_file)
		
		track_matches[input_file] = {
			'audio': [],
			'subtitles': [],
		}
		
		tracks = get_file_tracks(input_file)
		for track_type, tracks in tracks.items():
			print(f"{'-' * int(27 - len(track_type) / 2)} {track_type.capitalize()} {'-' * int(27 - len(track_type) / 2)}")
			
			nothing_selected = True
			
			for data in tracks:
				if PRINT_TRACK_INFO:
					print(data)
				
				selecting = True
				
				lang_index = match_track(data, 'language',   requirements[track_type]['lang_match'], requirements[track_type]['lang'])
				name_index = match_track(data, 'track_name', requirements[track_type]['name_match'], requirements[track_type]['name'])
				
				if lang_index >= 0 and name_index >= 0:
					weight = (lang_index + 1) * 10 + name_index
					track_matches[input_file][track_type].append( (weight, str(data['id'])) )
					
					print(f"SELECTED {data['id']}: PRI {name_index}   LANG '{data['language']}'  NAME '{data['track_name']}'")
					nothing_selected = False
					
				else:
					print(f"  ----   {data['id']}: PRI -   LANG '{data['language']}'  NAME '{data['track_name']}'")
			
			if nothing_selected:
				raise Exception(f"Nothing was selected for '{input_file}'")
			
		track_matches[input_file]['audio'] = sorted(track_matches[input_file]['audio'], key=lambda x: x[0])
		track_matches[input_file]['audio'] = [x[1] for x in track_matches[input_file]['audio']]
		
		track_matches[input_file]['subtitles'] = sorted(track_matches[input_file]['subtitles'], key=lambda x: x[0])
		track_matches[input_file]['subtitles'] = [x[1] for x in track_matches[input_file]['subtitles']]
		
		for track_type, tracks in track_matches[input_file].items():
			if requirements[track_type]['select'] == Select.FIRST_MATCH:
				track_matches[input_file][track_type] = tracks[0]
		
		print("\n--------------------\n")
		# break
except Exception as e:
	print("Fatal error:", e)
	exit()
	

def fprint(f, s):
	f.write(s)
	f.write("\n")
	# print(s)

with open("sifted_tracks.py", "w") as f:

	fprint(f, "keep_audio_tracks = {")
	for file, track_ids in track_matches.items():
		fprint(f, f"\t\"{file}\" : [{','.join(track_ids['audio'])}],")
	fprint(f, "}")
		
	fprint(f, "keep_subtitle_tracks = {")
	for file, track_ids in track_matches.items():
		fprint(f, f"\t\"{file}\" : [{', '.join(track_ids['subtitles'])}],")
	fprint(f, "}")
		
	fprint(f, "default_tracks = {")
	for file, track_ids in track_matches.items():
		fprint(f, f"\t\"{file}\" : [{', '.join([track_ids['audio'][0], track_ids['subtitles'][0]])}],")
	fprint(f, "}")
		
	fprint(f, "forced_tracks = {")
	for file, track_ids in track_matches.items():
		fprint(f, f"\t\"{file}\" : [{track_ids['audio'][0]}],")
	fprint(f, "}")

os.startfile("sifted_tracks.py")
