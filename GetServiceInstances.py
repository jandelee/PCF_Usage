#! python

import pcf_api, argparse

# get_service_instances.py generates a list of all the service instances being used within the current cf target environment.
# The details provided for each service instance include Org, Space, Service name, Service Plan name, and Service Instance GUID
# the Service Instance GUID can be used to match a service with a corresponding deployment tag attached to EC2 resources in AWS

parser = argparse.ArgumentParser(description='This script gathers info about each service instance in a PCF foundation')
parser.add_argument('-x', help='eXtended', action='store_true')
parser.add_argument('-v', help='verbose', action='store_true')
args = parser.parse_args()

#print("Getting orgs...")
org_names = pcf_api.build_dict( "/v2/organizations", 'name' )
#print("Getting spaces...")
space_names = pcf_api.build_dict( "/v2/spaces", 'name' )
space_org_guids = pcf_api.build_dict( "/v2/spaces", 'organization_guid' )
#print("Getting service plans...")
service_plan_names = pcf_api.build_dict( "/v2/service_plans", 'name' )
service_names = pcf_api.build_dict( "/v2/services", 'label' )

if (args.x):
	if (args.v):
		print("Getting apps")
	app_names = pcf_api.build_dict( "/v2/apps", 'name')
	if (args.v):
		print("Getting app guids by service")
	app_guids_by_service = pcf_api.build_dict_list( "/v2/service_bindings", "service_instance_guid", "app_guid")

#print("Looping through all service instances...")
items = pcf_api.get_items( "/v2/service_instances" )

print("Org,Space,Service,Service Plan,Service Instance GUID,Created At,Updated At", end="")
if (args.x):
	print(",Service Instance Name,Service Type,Bound App Count,Bound Apps")
else:
	print()

for item in items:
	service_instance_guid = item['metadata']['guid']
	created_at = item['metadata']['created_at']
	updated_at = item['metadata']['updated_at']
	if (updated_at is None):
		updated_at = ""
	service_guid = item['entity']['service_guid']
	service_plan_guid = item['entity']['service_plan_guid']
	space_guid = item['entity']['space_guid']
	org_guid = space_org_guids[space_guid]
	org_name = org_names[org_guid]
	space_name = space_names[space_guid]
	service_name = service_names[service_guid]
	service_plan_name = service_plan_names[service_plan_guid]
	#print(item['entity'])
	print( org_name + ',' + space_name + ',' + service_name + ',' + service_plan_name + ',' + service_instance_guid + ',' + created_at + ',' + updated_at, end="")
#	print( org_name + ',' + space_name + ',' + service_name + ',' + service_plan_name + ',' + service_instance_guid + ',' + created_at, end="")
	if (args.x):
		#if 'service_bindings_url' in item['entity']:
		print(",%s,%s" % (item['entity']['name'], item['entity']['type'], ), end="")
		if service_instance_guid in app_guids_by_service:
			apps = app_guids_by_service[service_instance_guid]
			print(",%d" % ( len(apps) ), end="")
			for app in apps:
				print("," + app_names[app], end="")
		else:
			print(",0", end="")
	print()
