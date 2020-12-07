import os
import glob

def load_file(filename, mode = "rb"):
	with open(filename, mode) as f:
		data = f.readlines()
		data = [x.decode('utf-8').strip() for x in data]
		return data
	
	return False

def save_file(filename, data):
	with open(filename, 'wb') as f:
		f.write(data.encode('utf-8'))

subs_files = glob.glob("*.ass")

FontIndex = 1
ShadowIndex = -6
OutlineIndex = -7

for subfile in subs_files:
	subs_data = load_file(subfile)
	if subs_data == False:
		print(f"Load error! {subfile}")
		break
		
	output_data = []

	for line in subs_data:
		if 'Style:' in line and not 'WrapStyle' in line:
			tokens = line.split(',')
			if ('Style: Default' in tokens[0]):
				continue
				
			if 'Style: Default' in tokens[0]:
				tokens[FontIndex] = 'Gandhi Sans'
				tokens[ShadowIndex] = '0'
				tokens[OutlineIndex] = '1'
			else:
				tokens[ShadowIndex] = '0'
				tokens[OutlineIndex] = '1' if int(tokens[OutlineIndex]) > 1 else '0'
			
			formatted = ','.join(tokens)
			output_data.append(formatted)
		else:
			output_data.append(line)
	
	output_filename = os.path.join('sub_output', subfile)
	save_file(output_filename, '\n'.join(output_data))
	
	print("Saved", output_filename)
	
	# break
