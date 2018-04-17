#! python

import pcf_api, openpyxl, datetime, dateutil.parser

# get_app_info.py retrieves app info for each app in PCF
#columns = ['Org','Space','App','App_GUID','Buildpack','Detected_Buildpack','App_State']
#df = pd.DataFrame(columns=columns)

today = datetime.datetime.now(datetime.timezone.utc)

filename = input('Enter the name of an Excel file to write the app info to => ')
if filename.find('.')<0:
	filename = filename + '.xlsx'
print('Writing app info to ' + filename)

print("Getting orgs...")
org_names = pcf_api.build_dict( "/v2/organizations", 'name' )
print("Getting spaces...")
space_names = pcf_api.build_dict( "/v2/spaces", 'name' )
space_org_guids = pcf_api.build_dict( "/v2/spaces", 'organization_guid' )
print("Getting app instances...")
items = pcf_api.get_items( "/v2/apps" )

buildpacks = {}
detected_buildpacks = {}

wb = openpyxl.Workbook()
ws = wb.active
ws.title = 'Apps' # Change the name of the default sheet to Apps
ws.append(['Org','Space','App','App_GUID','Buildpack','Detected_Buildpack','App_State','Created_At','Updated_At'])

# loop through all the items returned from the /v2/apps call
for item in items:
	app_guid = item['metadata']['guid']
	app_name = item['entity']['name']
	buildpack = item['entity']['buildpack']
	detected_buildpack = item['entity']['detected_buildpack']
	state = item['entity']['state']  # STARTED or STOPPED
	space_guid = item['entity']['space_guid']
	created_at = item['metadata']['created_at']
	updated_at = item['metadata']['updated_at']
	org_guid = space_org_guids[space_guid]
	org_name = org_names[org_guid]
	space_name = space_names[space_guid]
	delta_since_creation = today - dateutil.parser.parse(created_at)
	delta_since_creation = delta_since_creation.days
	if updated_at is not None:
		delta_since_updating = today - dateutil.parser.parse(updated_at)
		delta_since_updating = delta_since_updating.days
	else:
		delta_since_updating = 'None'
	ws.append([org_name, space_name, app_name, app_guid, buildpack, detected_buildpack, state, delta_since_creation, delta_since_updating])
	if state == 'STARTED':
		if buildpack is not None:
			if buildpack in buildpacks:
				buildpacks[buildpack] += 1
			else:
				buildpacks[buildpack] = 1
		if detected_buildpack is not None:
			if detected_buildpack in buildpacks:
				buildpacks[detected_buildpack] += 1
			else:
				buildpacks[detected_buildpack] = 1

ws = wb.create_sheet('Buildpacks')
ws.append(['Buildpack','Count'])
for bp in buildpacks:
	if len(bp)>1: # Ignore blanks
		ws.append([bp,buildpacks[bp]])

#ws = wb.create_sheet('Detected_Buildpacks')
#ws.append(['Detected_Buildpack','Count'])
#for bp in detected_buildpacks:
#	ws.append([bp,detected_buildpacks[bp]])

wb.save(filename)