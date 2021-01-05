import os

def convertToAscii(inputString, replace=" "):
	output = ""
	for c in inputString:
		if ord(c) < 128:
			output += c
		else:
			output += replace
	
	return output

for root, subdirs, files in os.walk("."):
	print(root)
	for file in files:
		originalPath = os.path.join(root, file)
		newPath = os.path.join(root, convertToAscii(file))
		if (originalPath != newPath):
			os.rename(originalPath, newPath)
			print("  Renamed: ", originalPath, " -> ", newPath)
	
	print("\n")
