import sys, pcf_api

# make sure we have exactly 3 file arguments
if len(sys.argv) != 4:
	print('Usage:', str(sys.argv[0]), 'usage_csv_file','services_csv_file','services_costs_file')
	print('   where usage_csv_file is a file containing the combined app usage for all environments')
	print('   where services_csv_file is a file containing the combined service instances being used in all environments')
	print('   where services_costs_file is a file containing the cost of each service for which charges are to be collected')
	exit()
else:
	usage_filename = sys.argv[1]
	svcs_filename = sys.argv[2]
	svcs_costs_filename = sys.argv[3]

# open the Licensed Services file and retrieve a list of licensed services
licensed_svcs = pcf_api.get_config_value( 'LICENSED_SERVICES' )
AWS_GB_MONTH = float(pcf_api.get_config_value( 'AWS_GB_MONTH' ))
PAS_LIC_MONTH = float(pcf_api.get_config_value( 'PAS_LIC_MONTH' ))
SVC_LIC_MONTH = float(pcf_api.get_config_value( 'SVC_LIC_MONTH' ))

# open the services costs file and build:
# dictionary containing the costs of each service/service plan where the key is the service/service plan
with open(svcs_costs_filename, 'rU') as svcs_costs_file:
	svcs_costs = {}
	line = svcs_costs_file.readline() # throw away the first line
	for line in svcs_costs_file.readlines(): # SvcName,SvcPlanName,Cost,TotalCost,SvcCount,AvgSvcInstances
		words = line.strip().split(',')
		svc_name_and_plan = words[0] + words[1]
		svcs_costs[svc_name_and_plan] = words[2]

# open the services file and build a dictionary where the key is the org and env and the value is the number of services for that org/env
num_services = {} # Total number of service instances used by an org in a given environment.  This is for informational purposes only and does not affect the costs charged to that org
licensed_services = {} # Number of PCF licensed services used by an org in a given environment.  Used to calculate the service licensing costs
service_costs = {} # Total AWS costs of services used by an org in a given environment.
with open(svcs_filename, 'rU') as services_file:
	line = services_file.readline() # throw away the first line
	for line in services_file.readlines():
		words = line.split(',')
		# Env,Org,Space,Service,Service Plan,Service Instance GUID
		key = words[1] + words[0]
		if not key in num_services.keys():
			num_services[key] = 1
		else:
			num_services[key] = num_services[key] + 1
		service_name_and_plan = words[3] + words[4]
		if service_name_and_plan in svcs_costs:
			if key in service_costs:
				service_costs[key] = service_costs[key] + float(svcs_costs[service_name_and_plan])
			else:
				service_costs[key] = float(svcs_costs[service_name_and_plan])
		if words[3] in licensed_svcs:
			if key in licensed_services:
				licensed_services[key] = licensed_services[key] + 1
			else:
				licensed_services[key] = 1

# open the usage file
with open(usage_filename, 'rU') as f:
	print("Org_Name,Env,Spaces,Apps,Instances,Total_GB_Used,Avg_GB_Used,Services,App AWS($),App Lic($),Svc AWS($),Svc Lic($),Total($)")
	line = f.readline() # throw away the first line
	for line in f.readlines():
		words = line.split(',')
		# Env,Org,Org_Usage,Org_Quota,Spaces,Running_Apps,Stopped_Apps,Total_Apps,Running_Instances,Stopped_Instances,Total_Instances

		if int(words[8]) > 0:
			avg_GB = int(words[2])/int(words[8])/1024
		else:
			avg_GB = 0.0
		key = words[1] + words[0]
		if key in num_services.keys():
			svc_count = num_services[key]
		else:
			svc_count = 0

		aws_cost = float(words[2])*AWS_GB_MONTH/1024
		app_lic_cost = float(words[8])*PAS_LIC_MONTH
		if key in service_costs.keys():
			service_cost = float(service_costs[key])
		else:
			service_cost = 0
		if key in licensed_services.keys():
			svc_lic_cost = licensed_services[key]*SVC_LIC_MONTH
		else:
			svc_lic_cost = 0
		total_cost = aws_cost + app_lic_cost + service_cost + svc_lic_cost
		if total_cost>0:
			print("%s,%s,%s,%s,%s,%.2f,%.2f,%d," % (words[1],words[0],words[4],words[5],words[8],int(words[2])/1024,avg_GB,svc_count), end="")
			print("%.2f,%.2f," % (aws_cost,app_lic_cost), end="")
			print("%d," % service_cost, end="")
			print("%d,%.2f" % (svc_lic_cost, total_cost))