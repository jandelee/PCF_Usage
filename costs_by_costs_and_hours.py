# costs_by_costs_and_hours.py
# This python script takes a csv file generated from the AWS billing console from the EC2 running hours costs and usage report.
# It produces a csv file with the key names in column 1, hours in column 2, and costs in column 3
import sys

# make sure we have exactly 1 argument 
if len(sys.argv) != 2:
	print('Usage:', str(sys.argv[0]), 'csv_file')
	print('   where csv_file is the file to be processed')
	exit()
else:
	filename = sys.argv[1]

with open(filename, 'rU') as f:
	# read the first line and save it in headings
	line = f.readline()
	# remove trailing \n
	line = line[:-1]
	headings = line.split(',')
	del headings[0] # throw away the first heading and total

	# read the second line (contains the totals)
	line = f.readline()
	# remove trailing \n
	line = line[:-1]
	totals = line.split(',')
	del totals[0]

	tag_costs = {}
	tag_hours = {}

	# loop through the headings and the totals
	for heading, total in zip(headings, totals):
		if heading[-3:] == '($)':
			tag_costs[heading[:-3]] = total
		elif heading[-5:] == '(Hrs)':
			tag_hours[heading[:-5]] = total
		else:
			print("Found invalid heading in csv file")
			print("Heading is: " + heading)
			exit()

	#print(tag_hours.keys())
	
	# print out the results
	for tag in tag_costs.keys():
		print( tag + ',' + tag_costs[tag] + ',' + tag_hours[tag] )
