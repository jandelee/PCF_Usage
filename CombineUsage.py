#! python
# CombineUsage.py takes as argument a date string, determines which files in the current directory match that date string, and combines those files
# into a single usage file that is suitable for input to the GenerateBilling.py script
# The environment is automatically extracted out of the filename by looking for text surrounded by dash characters.
# For example, given a filename UsageReport-MIL-OPS-20180311.csv, the text "MIL-OPS" will be the environment since that text has dashes on both sides

import sys, subprocess, os

# make sure we have exactly 3 arguments
if len(sys.argv) == 4:
	keyword = sys.argv[1]
	datestring = sys.argv[2]
	combinedfilename = sys.argv[3]
else:
	print('Usage:', str(sys.argv[0]), ' <keyword> <date-string> <combined_filename>')
	print('   where keyword represents a text string that must be present in the filename')
	print('   and where date-string is a date in the form YYYYMMDD')
	print('   the date-string is used to determine which files in the current directory will be combined in order to')
	print('   create a master usage file across multiple PCF environments')
	print('   and combined_filename is the name of the file that the combined usage information will be written to.')
	exit()

# get the files in the current directory
files = os.listdir('.')
matchingfiles = []

# Determine which ones match the datestring
for file in files:
	if file.find(keyword)>=0 and file.find(datestring)>0 and file[-4:] == '.csv' and file.find('-')>0:
		matchingfiles.append(file)

# Print out the matching files
print("The following .csv files in the current directory match the datestring:")
for filename in matchingfiles:
	print(filename)

result = input("Proceed? (Y/N) ")
if result == 'y' or result == 'Y':
	# open the combined file for output
	with open(combinedfilename, "w") as combined_file:
		header_processed = False
		for filename in matchingfiles:
			# split the filename on dashes
			words = filename.split('-')
			if len(words)>2:
				if len(words) == 3:
					pcfenv = words[1]
				elif len(words) == 4:
					pcfenv = words[1] + '-' + words[2]
				else:
					print("Filename " + filename + " contains too many dashes")
					exit()
				print("Processing " + filename + " with PCF environment of " + pcfenv)
				# open the file
				with open(filename, "r") as file:
					# read the header
					line = file.readline()
					if not header_processed:
						print('Env,' + line, file=combined_file, end='')
						header_processed = True
					for line in file:
						if line.find('Total for all orgs') != 0:
							print(pcfenv + ',' + line, end='', file=combined_file)
