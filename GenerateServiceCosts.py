#! python
# GenerateServiceCosts.py takes as input 1) AWS costs/deployment tag and 2) combined service instances list
# and calculates a cost for each service based on the average of AWS costs for each instance of that service

import sys, pcf_api
#import pandas as pd

# make sure we have exactly 3 arguments
if len(sys.argv) == 3:
	aws_costs_filename = sys.argv[1]
	services_filename = sys.argv[2]
else:
	print('Usage:', str(sys.argv[0]), 'aws_costs_csv_file services_csv_file')
	print('   where aws_costs_csv_file is a csv file containing the AWS costs by deployment tag')
	print('   and services_csv_file is a csv file containing the combined list of service instances')
	exit()

#df = pd.read_csv(services_filename)
#print(df.head())

# Read in the services file and build a dictionary where the key is the service GUID
# and the value is the service name/service plan name (separated by a comma)
with open(services_filename, 'rU') as services_file:
	services = {}
	line = services_file.readline() # Throw away the header
	for line in services_file.readlines():
		words = line.strip().split(',') # Env,Org,Space,Service,Service Plan,Service Instance GUID
		if len(words)>4:
			service_name_and_plan = words[3] + ',' + words[4] # combine the service name and the service plan name to make a key
			service_guid = words[5]
			services[service_guid] = service_name_and_plan

billed_services_tags = pcf_api.get_config_value( 'SERVICE_DEPLOYMENT_TAGS' )
svc_costs_filename = "svc_costs.csv"
print('Writing service costs to file ' + svc_costs_filename)
unmatched_guids_filename = "unmatched_guids.csv"
print("Writing unmatched GUID's to file " + unmatched_guids_filename)

# open the AWS costs file
with open(aws_costs_filename, 'rU') as aws_file, open(svc_costs_filename, 'w') as svc_costs_file, open(unmatched_guids_filename, 'w') as unmatched_guids_file:
	svc_costs = {}
	svc_counts = {}
	svc_instances = {}
	unmatched_guids = []
	# For each line in the AWS file
	# Format is Deployment Tag,Costs,Hours,Instances
	for line in aws_file.readlines():
		line = line.strip()

		found = False
		for tag in billed_services_tags:
			if line.startswith(tag):
				found = True
		if found:

#			print(line)
			# If this line is an on demand service
			if line.find('service-instance_') == 0:
				# Extract the GUID, if present
				words = line.split(',')
				guid = words[0][17:]
				if guid in services:
					service_name_and_plan = services[guid]
					if service_name_and_plan in svc_costs:
						svc_costs[service_name_and_plan] = svc_costs[service_name_and_plan] + float(words[1])
						svc_counts[service_name_and_plan] = svc_counts[service_name_and_plan] + 1
						svc_instances[service_name_and_plan] = svc_instances[service_name_and_plan] + float(words[3])
					else:
						svc_costs[service_name_and_plan] = float(words[1])
						svc_counts[service_name_and_plan] = 1
						svc_instances[service_name_and_plan] = float(words[3])
				else:
					unmatched_guids.append(guid + ',' + words[1])
			# This is a multi-tenant service
			else:
				pass
	print("SvcName,SvcPlanName,Cost,TotalCost,SvcCount,AvgSvcInstances", file=svc_costs_file)
	for key in svc_costs:
		svc_cost = float(svc_costs[key])/float(svc_counts[key])
		svc_instance = float(svc_instances[key])/float(svc_counts[key])
		print("%s,%.2f,%.2f,%d,%.2f" % (key, svc_cost, float(svc_costs[key]),svc_counts[key],svc_instance), file=svc_costs_file)
	print("GUID,Cost", file=unmatched_guids_file)
	for guid_and_cost in unmatched_guids:
		print(guid_and_cost, file=unmatched_guids_file)
