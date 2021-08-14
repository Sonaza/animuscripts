import os
import glob
import subprocess
import re

def pp(program_name): return os.path.join('F:\\Animu\\_Tools', program_name)
mkvmerge   = pp('mkvmerge')

FIX_VIDEO_TITLES = True
OVERWRITE_IMMEDIATELY = False

ADD_FONTS = True
COPY_ORIGINAL_ATTACHMENTS = False

MODIFY_TRACKS = True
try:
	from sifted_tracks import *
	print("Imported sifted_tracks.py\n")
	
except ImportError:
	print("Using defaults (sifted_tracks.py import failed)\n")
	
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

#----------------------------------------------------------

def comma_concat(list_items):
	return ','.join([str(x) for x in list_items])
	
def get_track_list(file, track_list):
	if file in track_list:
		return track_list[file]
	return track_list['default']
	
def strip_file_name(name):
	name, ext = os.path.splitext(name)
	disallowed_characters = re.escape('&"#!:-\'')
	name = name.lower()
	name = re.sub(r'([\[\(].*?[\]\)])', '', name).strip()
	name = re.sub('[' + disallowed_characters + ']', '', name)
	name = re.sub(r'( {2,}?)', ' ', name).strip()
	name = name.replace(' ', '_')
	return name
	
video_files = glob.glob("*.mkv")
subs_files = glob.glob("*.ass")
chapters_files = glob.glob("*.chapters.txt")
if len(chapters_files) < len(video_files):
	print(f"Using no chapters (found {len(chapters_files)} chapters files for {len(video_files)} video files)")
	print()
	chapters_files = [''] * len(video_files)
	
video_subs_map = list(zip(video_files, subs_files, chapters_files))

attachments_folder = "attachments"
attachments_root_fonts = glob.glob(os.path.join(attachments_folder, '*.ttf'))
attachments_root_fonts.extend(glob.glob(os.path.join(attachments_folder, '*.otf')))

def get_fonts(file_name):
	font_folder = os.path.join(attachments_folder, strip_file_name(file_name))
	if os.path.exists(font_folder) and os.path.isdir(font_folder):
		fonts = glob.glob(os.path.join(font_folder, '*.ttf'))
		fonts.extend(glob.glob(os.path.join(font_folder, '*.otf')))
		return fonts
	return attachments_root_fonts

font_mimes = dict(
	ttf = 'font/ttf',
	otf = 'font/otf'
)
def get_font_mime(fontfile):
	_, ext = os.path.splitext(fontfile)
	try:
		return font_mimes[ext[1:].lower()]
	except:
		print("Unknown font mime type:", fontfile)
		return 'font/ttf'

output_folder = "output"

add_subs_language = ('eng', 'English')

for input_video, input_subs, chapters_file in video_subs_map:
	output_name = f"{output_folder}/{input_video}"
	
	input_video_name, input_video_ext = os.path.splitext(input_video)
	
	chapters_flag = ''
	if len(chapters_file) > 0 and os.path.exists(chapters_file):
		chapters_flag = f'--chapters "{chapters_file}"'
		
	video_title_flag = ''
	if FIX_VIDEO_TITLES:
		video_title, _ = os.path.splitext(input_video)
		video_title_flag = f'--title "{video_title}"'
	
	fonts_flags = ''
	if ADD_FONTS:
		fonts_flags = ' '.join(f'--attachment-mime-type {get_font_mime(x)} --attach-file "{x}"' for x in get_fonts(input_video))
	
	audio_tracks_flag    = ''
	subtitle_tracks_flag = '-S'
	default_tracks_flag  = ''
	forced_tracks_flag   = ''
	if MODIFY_TRACKS:
		if len(keep_audio_tracks) > 0:
			audio_tracks_flag    = f'--audio-tracks {comma_concat(get_track_list(input_video, keep_audio_tracks))}'	
			
		# if len(keep_subtitle_tracks) > 0:
		# 	subtitle_tracks_flag = f'--subtitle-tracks {comma_concat(get_track_list(input_video, keep_subtitle_tracks))}'
			
		if len(default_tracks) > 0:
			default_tracks_flag = ' '.join([f'--default-track {x}' for x in get_track_list(input_video, default_tracks)])
			
		if len(forced_tracks) > 0:
			forced_tracks_flag  = ' '.join([f'--forced-track {x}' for x in get_track_list(input_video, forced_tracks)])
	
	subs_flags = f'--language "0:{add_subs_language[0]}" --track-name "0:{add_subs_language[1]}" --default-track 0:1 "{input_subs}"'
	
	attachments_copy_flag = ''
	if not COPY_ORIGINAL_ATTACHMENTS:
		attachments_copy_flag = '-M'
	
	input_flags = f'{video_title_flag} {audio_tracks_flag} {subtitle_tracks_flag} {default_tracks_flag} {forced_tracks_flag} {attachments_copy_flag}'
	addition_flags = f'{subs_flags} {fonts_flags} {chapters_flag}'
	
	command = f'{mkvmerge} -o "{output_name}" {input_flags} "{input_video}" {addition_flags}'
	print(command)
	subprocess.call(command, shell=True)
	
	print("\n--------------------\n-")
	# break
