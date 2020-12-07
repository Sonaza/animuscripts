import os
import glob
import subprocess

video_files = glob.glob("*.mkv")

output_folder = "output"

for input_video in video_files:		
	output_name = f"{output_folder}/{input_video}"
	if os.path.exists(output_name):
		continue
	
	video_title = input_video.split('.')[0]
	
	command = f'mkvmerge -o "{output_name}" "{input_video}" --title "{video_title}"'
	subprocess.call(command, shell=True)
	
	# print()
	# break
