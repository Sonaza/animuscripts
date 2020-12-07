import os
import glob
import subprocess
import errno
import math
import threading

def mkdir_p(path):
	try:
		os.makedirs(path)
	except OSError as exc:  # Python ≥ 2.5
		if exc.errno == errno.EEXIST and os.path.isdir(path):
			pass
		else:
			raise

video_files = glob.glob("*.mkv")

output_folder = "output2"
mkdir_p(output_folder)

funishit_duration_ms = 10050
overwrite_files = True

cbr_target = 19
vbr_average_kbit = 2500
vbr_maxrate_kbit = 3500

encoding_commands = []

TRY_THREADING_NONSENSE = False

video_files = [video_files[1]]
print(video_files)
# exit()

for input_video in video_files:
	output_name = f"{output_folder}/{input_video}"
	if os.path.exists(output_name) and not overwrite_files:
		print("Output file exists:", output_name, "(skipping)")
		continue
	
	skip_funishit_flag = ''
	if funishit_duration_ms > 0:
		skip_funishit_flag = f'-ss {funishit_duration_ms:d}ms'
	
	# video_flags = f'-c:v h264_nvenc -preset:v slow -profile:v high -level:v 4.0 -rc:v vbr -cq:v {cbr_target:d} -b:v {vbr_average_kbit:d}k -maxrate:v {vbr_maxrate_kbit}k -bf:v 3'
	video_flags = f'-c:v hevc_nvenc -preset:v llhq -profile:v main10 -tier:v high -spatial_aq:v 1 -level:v 4.0 -rc:v vbr -cq:v {cbr_target:d} -b:v {vbr_average_kbit:d}k -maxrate:v {vbr_maxrate_kbit}k'
	audio_flags = f'-c:a copy'
	
	command = f'ffmpeg.exe -y -threads 4 -hwaccel auto {skip_funishit_flag} -i "{input_video}" {video_flags} {audio_flags} "{output_name}"'
	encoding_commands.append(command)
	
	# print(command)
	# exit()
	break

if not TRY_THREADING_NONSENSE:
	for command in encoding_commands:
		print(command)
		subprocess.call(command, shell=True)
		print("\n--------------------\n")

else:
	def chunks(l, n):
		for i in range(0, len(l), n):
			yield l[i:i + n]

	num_threads = 1
	commands_per_thread = list(chunks(encoding_commands, max(1, math.floor(len(encoding_commands) / num_threads))))

	def encoding_thread(thread_commands):
		for command in thread_commands:
			print(command)
			subprocess.call(command, shell=True)
			print("\n--------------------\n")

	encoding_threads = []
	for thread_commands in commands_per_thread:
		new_thread = threading.Thread(target=encoding_thread, args=(thread_commands,), daemon=True)
		new_thread.start()
		encoding_threads.append(new_thread)

	for thread in encoding_threads:
		thread.join()
