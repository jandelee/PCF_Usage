import requests, subprocess, pcf_api

# get_service_instances.py generates a list of all the service instances being used within the current cf target environment.
# The details provided for each service instance include Org, Space, Service name, Service Plan name, and Service Instance GUID
# the Service Instance GUID can be used to match a service with a corresponding deployment tag attached to EC2 resources in AWS

# determine the API endpoint used in the current cf target
CP = subprocess.run(["cf", "target"], stdout=subprocess.PIPE)
if CP.returncode != 0:
	print("Error occurred executing 'cf target' command")
	exit()
result = CP.stdout.strip() # get the results of running the command and strip off the trailing newline
result = result.decode() # convert to string; result consists of multiple lines
lines = result.split('\n')
words = lines[0].split()
API_URL = words[2]

#print("Getting orgs...")
org_names = pcf_api.build_dict( API_URL, "/v2/organizations", 'name' )
#print("Getting spaces...")
space_names = pcf_api.build_dict( API_URL, "/v2/spaces", 'name' )
space_org_guids = pcf_api.build_dict( API_URL, "/v2/spaces", 'organization_guid' )
#print("Getting service plans...")
service_plan_names = pcf_api.build_dict( API_URL, "/v2/service_plans", 'name' )
service_names = pcf_api.build_dict( API_URL, "/v2/services", 'label' )

#print("Looping through all service instances...")
items = pcf_api.get_items( API_URL, "/v2/service_instances" )

print("Org,Space,Service,Service Plan,Service Instance GUID")
for item in items:
	service_instance_guid = item['metadata']['guid']
	service_guid = item['entity']['service_guid']
	service_plan_guid = item['entity']['service_plan_guid']
	space_guid = item['entity']['space_guid']
	org_guid = space_org_guids[space_guid]
	org_name = org_names[org_guid]
	space_name = space_names[space_guid]
	service_name = service_names[service_guid]
	service_plan_name = service_plan_names[service_plan_guid]
	print( org_name + ',' + space_name + ',' + service_name + ',' + service_plan_name + ',' + service_instance_guid )

exit()


	