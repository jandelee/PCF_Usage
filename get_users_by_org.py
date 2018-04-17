import pcf_api

# get_users_by_org.py generates a list of all the usernames for each of the users attached to each org within the current cf target environment.
# Note: On .io the usernames primarily are the GEOINT Services username.  On .mil, the usernames are the NGA email of the user.

org_names = pcf_api.get_data("/v2/organizations", 'name')
count=0
for guid in org_names: # guid is the key for the org_names dictionary
	print("Org: " + org_names[guid])
	labels = pcf_api.get_data("/v2/organizations/" + guid + "/users", 'username', silent=True)
	for label in labels.values():
		print("User: " + label)
	count = count + 1
