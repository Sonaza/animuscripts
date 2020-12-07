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

output_folder = "output"

extract_attachments = True

def format_track_name(name, language = ''):
	disallowed_characters = re.escape('&"#!:-\'')
	
	name = name.lower()
	
	name = name.replace(language, '')
	name = re.sub(r'([\[\(].*?[\]\)])', '', name).strip()
	
	name = re.sub('[' + disallowed_characters + ']', '', name)
	name = re.sub(r'( {2,}?)', ' ', name).strip()
	
	name = name.replace(' ', '_')
	return name

def find_extractable_tracks(file_path):
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
	
	return (tracks, attachments)

for input_file in video_files:
	print("Processing extraction from file", input_file)
	
	tracks, attachments = find_extractable_tracks(input_file)
	if len(tracks) == 0 and len(attachments) == 0:
		print("Nothing to extract from file:", input_file)
		print("")
		continue
	
	file_name, ext = os.path.splitext(input_file)
	
	track_flags = []
	for track in tracks:
		track_ext = text_codecs[track['codec_id']]
		multitrack_identifier = ''
		if len(tracks) > 1:
			multitrack_identifier = f"_{track['track_name']}_{track['language']}_t{track['id']:02d}"
		subtitle_file_name = f"{file_name}{multitrack_identifier}{track_ext}"
		# print(subtitle_file_name)
		
		track_flag = f"\"{track['id']}:{output_folder}/{subtitle_file_name}\""
		track_flags.append(track_flag)
	
	attachment_flags = []
	for attachment in attachments:
		attachment_flag = f"\"{attachment['id']}:{output_folder}/attachments/{attachment['file_name']}\""
		attachment_flags.append(attachment_flag)
	
	track_command = "tracks " + ' '.join(track_flags)
	attachment_command = "attachments " + ' '.join(attachment_flags)
	
	command = f'mkvextract "{input_file}" {track_command}'
	if extract_attachments:
		command = f'{command} {attachment_command}'
	
	# print(command)
	subprocess.call(command, shell=True)
	
	print("\n--------------------\n")
	# break
