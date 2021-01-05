import os
import glob
import subprocess
import json
import re

video_files = glob.glob("*.mkv")

text_codecs = {
	"S_TEXT/SSA": ".ssa",
	"S_TEXT/ASS": ".ass",
	"S_TEXT/UTF8": ".srt",
	"S_TEXT/ASCII": ".srt",
}

subs_output_folder = "subtitles"
attachments_output_folder = "attachments"

extract_attachments = True

def match_any_exact(needles, haystack):
	return any(x.lower() == haystack.lower() for x in needles)

def match_any_substr(needles, haystack):
	return any(x.lower() in haystack.lower() for x in needles)

def get_file_tracks(file_path):
	if not os.path.exists(file_path):
		print("File does not exist:", file_path)
		return ([], [])
	
	command = ['mkvmerge', '-i', '-F', 'json', file_path]
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
	EXACT  = 1
	SUBSTR = 2

PRINT_TRACK_INFO = False

requirements = {
	"audio" : {
		"lang"        : ['jpn'],
		"lang_match"  : Match.EXACT,
		
		"name"        : [''],
		"name_match"  : Match.EXACT,
	},
	
	"subtitles" : {
		"lang"        : ['eng'],
		"lang_match"  : Match.EXACT,
		
		"name"        : ['Kaleido-subs'],
		"name_match"  : Match.SUBSTR,
	},
}

track_matches = {}

for input_file in video_files:
	print("Processing info from file", input_file)
	
	track_matches[input_file] = {
		'audio': [],
		'subtitles': [],
	}
	
	tracks = get_file_tracks(input_file)
	for track_type, tracks in tracks.items():
		if PRINT_TRACK_INFO:
			print(track_type)
		
		for data in tracks:
			if PRINT_TRACK_INFO:
				print(data)
			
			if requirements[track_type]['lang_match'] == Match.SUBSTR:
				if not match_any_substr(requirements[track_type]['lang'], data['language']):
					continue
			elif requirements[track_type]['lang_match'] == Match.EXACT:
				if not match_any_exact(requirements[track_type]['lang'], data['language']):
					continue
			
			if requirements[track_type]['name_match'] == Match.SUBSTR:
				if not match_any_substr(requirements[track_type]['name'], data['track_name']):
					continue
			elif requirements[track_type]['name_match'] == Match.EXACT:
				if not match_any_exact(requirements[track_type]['name'], data['track_name']):
					continue
				
			track_matches[input_file][track_type].append(str(data['id']))
			
			print(f"Selected {data['id']}: LANG '{data['language']}'  NAME '{data['track_name']}'")
	
	print("\n--------------------\n")
		
	# break

# keep_audio_tracks = {
# 	'excepticon.mkv' : [3],
# }
# keep_subtitle_tracks = {
# 	'excepticon.mkv' : [8],
# }

print("keep_audio_tracks = {")
for file, track_ids in track_matches.items():
	print(f"\t'{file}' : [{','.join(track_ids['audio'])}],")
print("}")
	
print("keep_subtitle_tracks = {")
for file, track_ids in track_matches.items():
	print(f"\t'{file}' : [{', '.join(track_ids['subtitles'])}],")
print("}")
	
print("default_tracks = {")
for file, track_ids in track_matches.items():
	print(f"\t'{file}' : [{', '.join(track_ids['audio'] + track_ids['subtitles'])}],")
print("}")
	
print("forced_tracks = {")
for file, track_ids in track_matches.items():
	print(f"\t'{file}' : [{', '.join(track_ids['audio'])}],")
print("}")
