import os
import glob
import subprocess
import shutil

def comma_concat(list_items):
	return ','.join([str(x) for x in list_items])
	
keep_audio_tracks = [2]
keep_subtitle_tracks = [4]
default_tracks = [2, 4]
forced_tracks = [2]

video_files = glob.glob("*.mkv")

output_folder = "output"

keep_audio_tracks = [2]
keep_subtitle_tracks = [4]
default_tracks = [2, 4]
forced_tracks = [2]

fix_video_titles = False
OVERWRITE_IMMEDIATELY = False

for input_video in video_files:		
	output_name = f"{output_folder}/{input_video}"
	
	video_title_flag = ""
	if fix_video_titles:
		video_title = input_video.split('.')[0]
		video_title_flag = f'--title "{video_title}"'
	
	audio_tracks_flag    = f'--audio-tracks {comma_concat(keep_audio_tracks)}'
	subtitle_tracks_flag = f'--subtitle-tracks {comma_concat(keep_subtitle_tracks)}'
	
	default_tracks_flag = ' '.join([f'--default-track {x}' for x in default_tracks])
	forced_tracks_flag  = ' '.join([f'--forced-track {x}' for x in forced_tracks])
	
	command = f'mkvmerge -o "{output_name}" {video_title_flag} {audio_tracks_flag} {subtitle_tracks_flag} {default_tracks_flag} {forced_tracks_flag} "{input_video}"'
	print(command)
	
	subprocess.call(command, shell=True)
	
	if OVERWRITE_IMMEDIATELY:
		print("Overwriting original with the newly fixed file...")
		shutil.move(output_name, input_video)
	
	print("\n-----------------\n")
	# break
