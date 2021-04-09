import os
import glob
import subprocess

def pp(program_name): return os.path.join('F:\\Animu\\_Tools', program_name)
mkvmerge   = pp('mkvmerge')

video_files = glob.glob("*.mkv")
subs_files = glob.glob("*.ass")
video_subs_map = list(zip(video_files, subs_files))

fonts = glob.glob('fonts/*.ttf')
fonts.extend(glob.glob('fonts/*.otf'))

font_mimes = dict(
	ttf = 'application/x-truetype-font',
	otf = 'application/x-font-opentype'
)
def get_font_mime(fontfile):
	return font_mimes[fontfile.split('.')[-1].lower()]

fonts_flags = ' '.join(f'--attachment-mime-type {get_font_mime(x)} --attach-file "{x}"' for x in fonts)

output_folder = "output"

add_subs_language = ('eng', 'English')

for input_video, input_subs in video_subs_map:
	output_name = f"{output_folder}/{input_video}"
	
	subs_flags = f'--language "0:{add_subs_language[0]}" --track-name "0:{add_subs_language[1]}" --default-track 0:1 "{input_subs}"'
	
	command = f'{mkvmerge} -o "{output_name}" -S "{input_video}" {subs_flags} {fonts_flags}'
	print(command)
	subprocess.call(command, shell=True)
	
	print("\n--------------------\n-")
	# break
