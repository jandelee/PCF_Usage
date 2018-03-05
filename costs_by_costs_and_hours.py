# costs1.py
# This python script takes a csv file generated from the AWS billing console from the EC2 running hours costs and usage report.
# It produces a csv file with the key names in column 1, hours in column 2, and costs in column 3
import sys

# make sure we have exactly 1 argument 
if len(sys.argv) != 3:
	print('Usage:', str(sys.argv[0]), 'csv_file days')
	print('   where csv_file is the file to be processed')
	print('   and days is the number of billing days')
	exit()
else:
	filename = sys.argv[1]
	days = float(sys.argv[2])

with open(filename, 'rU') as f:
	# read the first line and save it in headings
	line = f.readline()
	# remove trailing \n
	line = line[:-1]
	headings = line.split(',')
	del headings[0] # throw away the first heading

	# read the second line (contains the totals)
	line = f.readline()
	# remove trailing \n
	line = line[:-1]
	totals = line.split(',')
	del totals[0] # throw away the first total

	tag_costs = {}
	tag_hours = {}
	service_costs = 0.0
	service_hours = 0.0
	print('Deployment Tag,Costs,Hours,Instances')

	# loop through the headings and the totals
	for heading, total in zip(headings, totals):
		if heading[0:5] != 'Total':
			if heading[-3:] == '($)':
				tag_costs[heading[:-3]] = total
				if heading[:16] == 'service-instance':
					service_costs = service_costs + float(total)
			elif heading[-5:] == '(Hrs)':
				tag_hours[heading[:-5]] = total
				if heading[:16] == 'service-instance':
					service_hours = service_hours + float(total)
			else:
				print("Found invalid heading in csv file")
				print("Heading is: " + heading)
				exit()
		else:
			if heading[-3:] == '($)':
				tag_costs['Total'] = total
			elif heading[-5:] == '(Hrs)':
				tag_hours['Total'] = total
			else:
				print("Found invalid heading in csv file")
				print("Heading is: " + heading)
				exit()
				
	# print out the results
	for tag in tag_costs.keys():
		print( "%s,%s,%s,%.1f" % (tag,tag_costs[tag],tag_hours[tag],(float(tag_hours[tag])/days/24)))
	print( 'Service Subtotal,%.2f,%.2f,%.1f' % (service_costs,service_hours,(float(service_hours)/days/24)))
	print( 'Service Percentage,%.1f,%.1f' % ( (100*service_costs/float(tag_costs['Total'])), (100*service_hours/float(tag_hours['Total'])) ))
