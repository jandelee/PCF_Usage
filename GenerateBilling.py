import sys

# make sure we have exactly 3 file argument 
if len(sys.argv) != 4:
	print('Usage:', str(sys.argv[0]), 'usage_csv_file','services_csv_file','service summary file')
	print('   where usage_csv_file is a usage file')
	print('   where services_csv_file is a services file')
	print('   where services summary file is a services summary file')
	exit()
else:
	usage_filename = sys.argv[1]
	services_filename = sys.argv[2]
	services_summary_filename = sys.argv[3]

# open the services summary file and build:
# dictionary containing the costs of each service/service plan where the key is the service/service plan
# list of the services that require a license
with open(services_summary_filename, 'rU') as summary_file:
	service_plan_costs = {}
	licensed_service = []
	line = summary_file.readline() # throw away the first line
	for line in summary_file.readlines():
		line = line.strip()
		words = line.split(',')
		if words[0] != "": # This is a service line
			service = words[0]
			if line[-1:] == "1":
				licensed_service.append(service)
		elif words[2] != "": # This is a service plan line
			plan = words[2]
			plan_cost = words[4]
			if plan_cost != "":
				if plan_cost[:1] == '$':
					plan_cost = plan_cost[1:]
				service_plan = service + plan
				service_plan_costs[service_plan] = plan_cost 
		else: # invalid line
			print( "Invalid line found in services summary file:")
			print(line)
			exit()

# open the services file and build a dictionary where the key is the org and env and the value is the number of services for that org/env
num_services = {}
with open(services_filename, 'rU') as services_file:
	line = services_file.readline() # throw away the first line
	for line in services_file.readlines():
		words = line.split(',')
		# Env,Org,Space,Service,Service Plan,Service Instance GUID
		key = words[1] + words[0]
		if not key in num_services.keys():
			num_services[key] = 1
		else:
			num_services[key] = num_services[key] + 1

with open(usage_filename, 'rU') as f:
	print("Org_Name,Env,Spaces,Apps,Instances,Total_GB_Used,Avg_GB_Used")
	line = f.readline() # throw away the first line
	for line in f.readlines():
		words = line.split(',')
		# Env,Org,Org_Usage,Org_Quota,Spaces,Running_Apps,Stopped_Apps,Total_Apps,Running_Instances,Stopped_Instances,Total_Instances

		if int(words[8]) > 0:
			avg_GB = int(words[2])/int(words[8])/1024
		else:
			avg_GB = 0.0
		print("%s,%s,%s,%s,%s,%.2f,%.2f," % (words[1],words[0],words[4],words[5],words[8],int(words[2])/1024,avg_GB), end="")
		key = words[1] + words[0]
		if key in num_services.keys():
			print(num_services[key])
		else:
			print("0")
