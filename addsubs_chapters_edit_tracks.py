import os
import glob
import subprocess

def pp(program_name): return os.path.join('F:\\Animu\\_Tools', program_name)
mkvmerge   = pp('mkvmerge')

FIX_VIDEO_TITLES = False
OVERWRITE_IMMEDIATELY = False

ADD_FONTS = True
COPY_ORIGINAL_ATTACHMENTS = False

MODIFY_TRACKS = False
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
	
video_files = glob.glob("*.mkv")
subs_files = glob.glob("*.ass")
video_subs_map = list(zip(video_files, subs_files))

fonts = glob.glob('attachments/*.ttf')
fonts.extend(glob.glob('attachments/*.otf'))
font_mimes = dict(
	ttf = 'application/x-truetype-font',
	otf = 'application/x-font-opentype'
)
def get_font_mime(fontfile):
	_, ext = os.path.splitext(fontfile)
	try:
		return font_mimes[ext[1:].lower()]
	except:
		print("Unknown font mime type:", fontfile)
		return 'application/x-truetype-font'

fonts_flags = ''
if ADD_FONTS:
	fonts_flags = ' '.join(f'--attachment-mime-type {get_font_mime(x)} --attach-file "{x}"' for x in fonts)

output_folder = "output"

add_subs_language = ('eng', 'English')

for input_video, input_subs in video_subs_map:
	output_name = f"{output_folder}/{input_video}"
	
	input_video_name, input_video_ext = os.path.splitext(input_video)
	
	chapters_flag = ''
	chapters_file = f'{input_video_name}.chapters.txt'
	if os.path.exists(chapters_file):
		chapters_flag = f'--chapters "{chapters_file}"'
		
	video_title_flag = ''
	if FIX_VIDEO_TITLES:
		video_title, _ = os.path.splitext(input_video)
		video_title_flag = f'--title "{video_title}"'
	
	audio_tracks_flag    = ''
	subtitle_tracks_flag = '-S'
	default_tracks_flag  = ''
	forced_tracks_flag   = ''
	if MODIFY_TRACKS:
		if len(keep_audio_tracks) > 0:
			audio_tracks_flag    = f'--audio-tracks {comma_concat(keep_audio_tracks)}'
			
		if len(keep_subtitle_tracks) > 0:
			subtitle_tracks_flag = f'--subtitle-tracks {comma_concat(keep_subtitle_tracks)}'
			
		if len(default_tracks) > 0:
			default_tracks_flag  = ' '.join([f'--default-track {x}' for x in default_tracks])
			
		if len(forced_tracks) > 0:
			forced_tracks_flag   = ' '.join([f'--forced-track {x}' for x in forced_tracks])
	
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
