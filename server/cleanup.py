from os import listdir
from os.path import isfile, join
import os

onlyfiles = [f for f in listdir('./') if isfile(join('./', f))]


for files in onlyfiles:
	print(files, type(files))
	if 'npz' in files:
		print("***************************************************")
		current_file = os.path.basename(files)
		parent = os.path.dirname(os.path.abspath(files))
		print(parent)
		try:
			os.rename(files, parent + "\\graph data\\" + current_file)
			print(files)
		except:
			pass