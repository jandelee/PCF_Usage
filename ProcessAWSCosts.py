#!python
# ProcessAWSCosts.py - this script takes a csv file generated from the AWS billing console using the
# "Monthly EC2 running hours costs and usage" report and changes it from horizontal format to vertical format
# In the AWS csv file, the first line is a heading line that contains the deployment tags,
# the second line contains the Total costs and hours,
# and the third and subsequent lines (if present) contain the costs and hours for each calendar month in the AWS report.
# The resulting CSV file contains the deployment tag in column 1, hours in column 2, and costs in column 3
# In column 4, the # of instances is computed simply by dividing
# The last 3 lines of the resulting CSV file contain the Totals, Service Subtotals, and Service percentage of the Totals.

import sys, pcf_api

# make sure we have exactly 3 arguments
if len(sys.argv) == 3:
	input_filename = sys.argv[1]
	days = float(sys.argv[2])
else:
	print('Usage:', str(sys.argv[0]), 'csv_file days')
	print('   where csv_file is the file to be processed')
	print('   and days is the number of billing days in the month being processed')
	exit()

# open the Service Deployment Tags file and retrieve the list of Deployment tags for the billed services
billed_services_tags = pcf_api.get_config_value( 'SERVICE_DEPLOYMENT_TAGS' )
#for line in billed_services_tags:
#	print(line)
#exit()

if input_filename[0:2] == '.\\':
	input_filename = input_filename[2:]
file_name,file_ext = input_filename.split('.')
output_filename = file_name + '_processed.' + file_ext
print('Writing result to file ' + output_filename)

# open the AWS csv file
with open(input_filename, 'rU') as f, open(output_filename, 'w') as output_file:

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
	print('Deployment Tag,Costs,Hours,Instances', file=output_file)

	# loop through the headings and the totals
	for heading, total in zip(headings, totals):

		# Headings are in the form of: <deploymentTag>($), Total cost ($), <deploymentTag>(Hrs), Total usage (Hrs)
		# If the heading is 'Total cost ($)'
		if heading == 'Total cost ($)':
			tag_costs['Total'] = total

		# Else if the heading is 'Total usage (Hrs)'
		elif heading == 'Total usage (Hrs)':
			tag_hours['Total'] = total

		# Else if the heading ends with ($)
		elif heading[-3:] == '($)':
			tag_costs[heading[:-3]] = total
			found = False
			for tag in billed_services_tags:
				if heading.startswith(tag):
					found = True
			if found:
				service_costs = service_costs + float(total)

		# Else if the heading ends with (Hrs)
		elif heading[-5:] == '(Hrs)':
			tag_hours[heading[:-5]] = total
			found = False
			for tag in billed_services_tags:
				if heading.startswith(tag):
					found = True
			if found:
				service_hours = service_hours + float(total)

		# Else we found something unexpected in the heading
		else:
			print("Found invalid heading in csv file")
			print("Heading is: " + heading)
			exit()
	# If the hours data is present (costs data is also present)
	if len(tag_hours)>0:
		# print out the costs and hours results
		for tag in tag_costs.keys():
			print( "%s,%.2f,%.2f,%.1f" % (tag,float(tag_costs[tag]),float(tag_hours[tag]),(float(tag_hours[tag])/days/24)), file=output_file)
		print( 'Service Subtotal,%.2f,%.2f,%.1f' % (service_costs,service_hours,(float(service_hours)/days/24)), file=output_file)
		print( 'Service Percentage,%.1f,%.1f' % ( (100*service_costs/float(tag_costs['Total'])), (100*service_hours/float(tag_hours['Total'])) ), file=output_file)
	# Else only the cost data is present
	else:
		# print out the costs results
		for tag in tag_costs.keys():
			print( "%s,%.2f,%.2f,%.1f" % (tag.strip(),float(tag_costs[tag]),0.0,0.0), file=output_file)
		print( 'Service Subtotal,%.2f,%.2f,%.1f' % (service_costs,service_hours,(float(service_hours)/days/24)), file=output_file)
		print( 'Service Percentage,%.1f,%.1f' % ( (100*service_costs/float(tag_costs['Total'])), 0.0 ), file=output_file)
