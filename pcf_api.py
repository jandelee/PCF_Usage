import requests, subprocess

def show( pcf_cc_api_url, route ):
	# run a subprocess to get the oauth token
	CP = subprocess.run(["cf", "oauth-token"], stdout=subprocess.PIPE)
	if CP.returncode != 0:
		print("Error occurred attempting to retrieve oauth token")
		exit()
	result = CP.stdout.strip() # get the results of running the command and strip off the trailing newline
	token = result.decode() # convert to string; this is a bearer token

	# build the header we will use in the request
	headers = {"Authorization":token}

	# call the PCF CC API, using the header with the bearer token
	res = requests.get(pcf_cc_api_url + route, headers=headers)
	if res.status_code != 200:
		res.raise_for_status()

	# convert the result to json
	js = res.json()
	resources = js['resources']

	print(resources)

def show_data( pcf_cc_api_url, route ):
	# run a subprocess to get the oauth token
	CP = subprocess.run(["cf", "oauth-token"], stdout=subprocess.PIPE)
	if CP.returncode != 0:
		print("Error occurred attempting to retrieve oauth token")
		exit()
	result = CP.stdout.strip() # get the results of running the command and strip off the trailing newline
	token = result.decode() # convert to string; this is a bearer token

	# build the header we will use in the request
	headers = {"Authorization":token}

	done = False
	while not done:
		# call the PCF CC API, using the header with the bearer token
		res = requests.get(pcf_cc_api_url + route, headers=headers)
		if res.status_code != 200:
			res.raise_for_status()

		# convert the result to json
		js = res.json()

		resources = js['resources']
		# loop through the items in the resources list
		for r in resources:
			print(r)

		# If there is no next url then we are done
		next_url = js['next_url']
		if next_url == None:
			done = True
		else: # else use the next url for the route and do it again
			route = next_url

def get_data( pcf_cc_api_url, route, entity_name, return_guids, silent=None ):
	# run a subprocess to get the oauth token
	CP = subprocess.run(["cf", "oauth-token"], stdout=subprocess.PIPE)
	if CP.returncode != 0:
		print("Error occurred attempting to retrieve oauth token")
		exit()
	result = CP.stdout.strip() # get the results of running the command and strip off the trailing newline
	token = result.decode() # convert to string; this is a bearer token

	# build the header we will use in the request
	headers = {"Authorization":token}

	guids = []
	names = []
	done = False
	while not done:
		# call the PCF CC API, using the header with the bearer token
#		res = requests.get(pcf_cc_api_url + route, headers=headers, verify=False)
		res = requests.get(pcf_cc_api_url + route, headers=headers, verify='C:/Users/Family/Downloads/download.cer')
		if res.status_code != 200:
			res.raise_for_status()

		# convert the result to json
		js = res.json()

		resources = js['resources']
		# loop through the items in the resources list
		for r in resources:
#			print (r['metadata'])
#			print (r['entity'])
			guid = r['metadata']['guid']
			if guid != 'undefined':
				guids.append(guid)
				if entity_name in r['entity']:
					org_name = r['entity'][entity_name]
					names.append(org_name)
				else:
					if silent != True:
						print("Could not find " + entity_name + " in:")
						print(r['entity'])
					names.append('unknown')

		# If there is no next url then we are done
		next_url = js['next_url']
		if next_url == None:
			done = True
		else: # else use the next url for the route and do it again
			route = next_url

	if return_guids:
		return guids, names
	else:
		return names

def get_items( pcf_cc_api_url, route ):
	# run a subprocess to get the oauth token
	CP = subprocess.run(["cf", "oauth-token"], stdout=subprocess.PIPE)
	if CP.returncode != 0:
		print("Error occurred attempting to retrieve oauth token")
		exit()
	result = CP.stdout.strip() # get the results of running the command and strip off the trailing newline
	token = result.decode() # convert to string; this is a bearer token

	# build the header we will use in the request
	headers = {"Authorization":token}

	item_list = []
	done = False
	while not done:
		# call the PCF CC API, using the header with the bearer token
		res = requests.get(pcf_cc_api_url + route, headers=headers, verify='C:/Users/Family/Downloads/download.cer')
		if res.status_code != 200:
			res.raise_for_status()

		# convert the result to json
		js = res.json()

		resources = js['resources']

		item_list.extend( resources )

		# If there is no next url then we are done
		next_url = js['next_url']
		if next_url == None:
			done = True
		else: # else use the next url for the route and do it again
			route = next_url

	return item_list

def build_dict( pcf_cc_api_url, route, entity_name ):
	# run a subprocess to get the oauth token
	CP = subprocess.run(["cf", "oauth-token"], stdout=subprocess.PIPE)
	if CP.returncode != 0:
		print("Error occurred attempting to retrieve oauth token")
		exit()
	result = CP.stdout.strip() # get the results of running the command and strip off the trailing newline
	token = result.decode() # convert to string; this is a bearer token

	# build the header we will use in the request
	headers = {"Authorization":token}

	d = {}
	done = False
	while not done:
		# call the PCF CC API, using the header with the bearer token
		res = requests.get(pcf_cc_api_url + route, headers=headers, verify='C:/Users/Family/Downloads/download.cer')
		if res.status_code != 200:
			res.raise_for_status()

		# convert the result to json
		js = res.json()

		resources = js['resources']
		# loop through the items in the resources list
		for r in resources:
			guid = r['metadata']['guid']
			if entity_name in r['entity']:
				org_name = r['entity'][entity_name]
				d[guid] = org_name
			else:
				print("Could not find " + entity_name + " in:")
				print(r['entity'])
				d[guid] = 'unknown'

		# If there is no next url then we are done
		next_url = js['next_url']
		if next_url == None:
			done = True
		else: # else use the next url for the route and do it again
			route = next_url

	return d