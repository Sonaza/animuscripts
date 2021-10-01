import os
import glob
import subprocess
import json
import re

def pp(program_name): return os.path.join('F:\\Animu\\_Tools', program_name)
mkvmerge   = pp('mkvmerge')
mkvextract = pp('mkvextract')

video_files = glob.glob("*.mkv")

text_codecs = {
	"S_TEXT/SSA": ".ssa",
	"S_TEXT/ASS": ".ass",
	"S_TEXT/UTF8": ".srt",
	"S_TEXT/ASCII": ".srt",
}

subtitles_output_root = "subtitles"
attachments_output_root = "attachments"

EXTRACT_ATTACHMENTS = True
EXTRACT_ATTACHMENTS_TO_INDIVIDUAL_FOLDERS = False

EXTRACT_CHAPTERS = False

def format_track_name(name, language = ''):
	disallowed_characters = re.escape('&"#!:-\'')
	
	name = name.lower()
	
	name = name.replace(language, '')
	name = re.sub(r'([\[\(].*?[\]\)])', '', name).strip()
	
	name = re.sub('[' + disallowed_characters + ']', '', name)
	name = re.sub(r'( {2,}?)', ' ', name).strip()
	
	name = name.replace(' ', '_')
	return name

def strip_file_name(file_name):
	return format_track_name(file_name)

def find_extractable_tracks(file_path):
	if not os.path.exists(file_path):
		print("File does not exist:", file_path)
		return ([], [], 0)
	
	command = [mkvmerge, '-i', '-F', 'json', file_path]
	output = subprocess.check_output(command, stderr=subprocess.STDOUT).decode("utf-8")
	
	try:
		data = json.loads(output)
	except json.JSONDecodeError as e:
		print("Failed to parse mkvmerge output:", e)
		return ([], [], 0)
	
	tracks = []
	for track_info in data['tracks']:
		if track_info['type'] != 'subtitles':
			continue
		
		codec_id = track_info['properties']['codec_id']
		if not codec_id in text_codecs:
			print("Subtitle codec not supported:", codec_id)
			continue
		
		track_name = ''
		if 'track_name' in track_info['properties']:
			track_name = format_track_name(track_info['properties']['track_name'], track_info['properties']["language"])
		
		info = {
			"id":         track_info['id'],
			"codec_id":   codec_id,
			"track_name": track_name,
			"language":   track_info['properties']["language"]
		}
		tracks.append(info)
	
	attachments = []
	for attachment_info in data['attachments']:
		info = {
			"mime": attachment_info['content_type'],
			"id": attachment_info['id'],
			"file_name": attachment_info['file_name']
		}
		attachments.append(info)

	num_chapters = 0
	try:
		num_chapters = data['chapters'][0]['num_entries']
	except:
		pass
	
	return (tracks, attachments, num_chapters)

for input_file in video_files:
	print("Processing extraction from file", input_file)
	
	tracks, attachments, num_chapters = find_extractable_tracks(input_file)
	
	if len(tracks) == 0 and len(attachments) == 0 and num_chapters == 0:
		print("Nothing to extract from file:", input_file)
		print("")
		continue
	
	file_name, ext = os.path.splitext(input_file)
	
	tracks_command = ""
	if len(tracks) > 0:
		track_flags = []
		for track in tracks:
			track_ext = text_codecs[track['codec_id']]
			multitrack_identifier = ''
			if len(tracks) > 1:
				multitrack_identifier = f"_{track['track_name']}_{track['language']}_t{track['id']:02d}"
			subtitle_file_name = f"{file_name}{multitrack_identifier}{track_ext}"
			# print(subtitle_file_name)
			
			track_flag = f"\"{track['id']}:{subtitles_output_root}/{subtitle_file_name}\""
			track_flags.append(track_flag)
		
		tracks_command = f"tracks {' '.join(track_flags)}"
	
	chapters_command = ""
	if EXTRACT_CHAPTERS and num_chapters > 0:
		chapters_file = f"{file_name}.chapters.txt"
		chapters_command = f'chapters -s "{chapters_file}"'
	
	attachments_command = ""
	if EXTRACT_ATTACHMENTS and len(attachments) > 0:
		attachments_output_folder = attachments_output_root
		if EXTRACT_ATTACHMENTS_TO_INDIVIDUAL_FOLDERS:
			attachments_output_folder = os.path.join(attachments_output_folder, strip_file_name(file_name))
		
		attachment_flags = []
		for attachment in attachments:
			attachment_flag = f"\"{attachment['id']}:{attachments_output_folder}/{attachment['file_name']}\""
			attachment_flags.append(attachment_flag)
			
		attachments_command = f"attachments {' '.join(attachment_flags)}"
	
	command = f'{mkvextract} "{input_file}" {tracks_command} {chapters_command} {attachments_command}'
	
	# print(command)
	subprocess.call(command, shell=True)
	
	print("\n--------------------\n")
	# break
