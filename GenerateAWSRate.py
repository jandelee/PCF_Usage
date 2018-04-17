import sys, pcf_api

# make sure we have exactly 3 file arguments
if len(sys.argv) != 3:
	print('Usage:', str(sys.argv[0]), 'combined_usage_csv_file','AWS_processed_csv_file')
	print('   where combined_usage_csv_file is a file containing the combined app usage for all environments')
	print('   where AWS_processed_csv_file is a file containing the processed AWS data')
	exit()
else:
	usage_filename = sys.argv[1]
	aws_filename = sys.argv[2]

# open the usage file
with open(usage_filename, 'rU') as f:
	total_usage = 0.0
	line = f.readline() # throw away the first line
	for line in f.readlines():
		words = line.split(',')
		# Env,Org,Org_Usage,Org_Quota,Spaces,Running_Apps,Stopped_Apps,Total_Apps,Running_Instances,Stopped_Instances,Total_Instances
#		print(words[2])
		total_usage = total_usage + float(words[2])

# open the AWS processed file
with open(aws_filename, 'rU') as f:
	line = f.readline() # throw away the first line
	for line in f.readlines():
		words = line.split(',')
		if words[0] == 'Service Subtotal':
			service_cost = float(words[1])
		elif words[0] == 'Total':
			total_cost = float(words[1])
#total_cost = input('Enter the total AWS costs across dev and ops:')
#total_cost = float(total_cost)
app_cost = total_cost - service_cost
total_usage = total_usage/1024
print('Total AWS cost:' + str(total_cost))
print('Total service cost:' + str(service_cost))
print('Total app cost:' + str(app_cost))
print('Total Memory Usage (GB):' + str(total_usage))
print('$/GB-Month:' + str(app_cost/total_usage))
