import requests, subprocess, pcf_api

# get_users_by_org.py generates a list of all the usernames for each of the users attached to each org within the current cf target environment.
# Note: On .io the usernames primarily are the GEOINT Services username.  On .mil, the usernames are the NGA email of the user.

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

guids, names = pcf_api.get_data(API_URL, "/v2/organizations", 'name', True)
count=0
for guid, name in zip(guids, names):
	print("Org: " + name)
	labels = pcf_api.get_data(API_URL, "/v2/organizations/" + guid + "/users", 'username', False, True)
	for label in labels:
		print("User: " + label)
	count = count + 1
#	if (count>3):
#		exit()

exit()
#	gs, labels = pcf_api.get_data(API_URL, "/v2/organizations/" + guid + "/users", 'username', True)
#	for g, label in zip(gs, labels):
#		print("User: " + label)



results = js['total_results']
print("Total results=>" + str(results))
pages = js['total_pages']
print("Total pages=>" + str(pages))

r = js['resources']
for i in r:
	guid = i['metadata']['guid']
	print("guid=>" + guid + " label=>" + i['entity']['label'] + " active=>" + str(i['entity']['active']) + " bindable=>" + str(i['entity']['bindable']))
	plans = requests.get("https://api.system.dev.east.paas.geointservices.io/v2/services/" + guid + "/service_plans", headers=headers)
	plans = plans.json()
	plans_resources = plans['resources']
	print(len(plans_resources))
	print(plans_resources)
	for j in plans_resources:
		print(j['entity']['name'] + " " + j['entity']['description'])
	

	