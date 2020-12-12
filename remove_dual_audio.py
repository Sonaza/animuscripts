import os
import glob
import subprocess
import shutil

# Use per file exceptions to the dicts by specifying a file name as the key and adding a list of tracks for it
keep_audio_tracks = {
	'default' : [2],
	'excepticon.mkv' : [2],
}
keep_subtitle_tracks = {
	'default' : [4],
	'excepticon.mkv' : [4],
}
default_tracks = {
	'default' : [2, 4],
	'excepticon.mkv' : [2, 4],
}
forced_tracks = {
	'default' : [2],
	'excepticon.mkv' : [2],
}

def comma_concat(list_items):
	return ','.join([str(x) for x in list_items])

def get_track_list(file, track_list):
	if file in track_list:
		return track_list[file]
	return track_list['default']

video_files = glob.glob("*.mkv")

output_folder = "output"

fix_video_titles = False
OVERWRITE_IMMEDIATELY = False

for input_video in video_files:		
	output_name = f"{output_folder}/{input_video}"
	if os.path.exists(output_name): continue
	
	video_title_flag = ""
	if fix_video_titles:
		video_title = input_video.split('.')[0]
		video_title_flag = f'--title "{video_title}"'
		
	audio_tracks_flag    = f'--audio-tracks {comma_concat(get_track_list(input_video, keep_audio_tracks))}'	
	subtitle_tracks_flag = f'--subtitle-tracks {comma_concat(get_track_list(input_video, keep_subtitle_tracks))}'
	
	default_tracks_flag = ' '.join([f'--default-track {x}' for x in get_track_list(input_video, default_tracks)])
	forced_tracks_flag  = ' '.join([f'--forced-track {x}' for x in get_track_list(input_video, forced_tracks)])
	
	command = f'mkvmerge -o "{output_name}" {video_title_flag} {audio_tracks_flag} {subtitle_tracks_flag} {default_tracks_flag} {forced_tracks_flag} "{input_video}"'
	print(command)
	
	subprocess.call(command, shell=True)
	
	if OVERWRITE_IMMEDIATELY:
		print("Overwriting original with the newly fixed file...")
		shutil.move(output_name, input_video)
	
	print("\n-----------------\n")
	# break
