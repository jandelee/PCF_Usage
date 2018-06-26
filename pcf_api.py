import requests, subprocess

# This function searches the PlatformChargeback.cfg file for the key specified as the function argument and returns its value
# if found.  If the value is not found, the function terminates
def get_config_value( config_key ):
	with open("PlatformChargeback.cfg", 'rU') as config_file:
		result = ""
		results = {}
		for line in config_file.readlines():
			# If this is not a comment line
			if not line.startswith('#'):
				# If this line contains the ':' character, it contains at least a key, and possibly a value
				if line.find(':')>0:
					# If there is a previous result
					if len(result)>0:
						results[key] = result
						result = ""
#					print('*' + line + '*')
#					print(line.strip().split(':',1))
					key,value = line.strip().split(':',1)
					value = value.strip()
					# If the value of the key was specified on this line
					if len(value)>0:
						result = value
					else:
						result = []
				# Else this line only contains a value
				else:
					result.append( line.strip() )
		# If there is a previous result
		if len(result)>0:
			results[key] = result
			result = ""
		if config_key in results:
			return results[config_key]
		else:
			print('Did not find key ' + config_key + ' in PlatformChargeback.cfg')
			exit()

# get_cc_api_url runs the "cf target" command and extracts the Cloud Controller API URL from the result
def get_cc_api_url():
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
	return API_URL

# build_headers queries the cf cli to obtain the oauth token and constructs the headers necessary to pass that token
# through to the CC API as a bearer token
def build_headers():
	# run a subprocess to get the oauth token
	CP = subprocess.run(["cf", "oauth-token"], stdout=subprocess.PIPE)
	if CP.returncode != 0:
		print("Error occurred attempting to retrieve oauth token")
		exit()
	result = CP.stdout.strip() # get the results of running the command and strip off the trailing newline
	token = result.decode() # convert to string; this is a bearer token

	# build the header we will use in the request
	headers = {"Authorization":token}
	return headers

# show displays the result of calling the CC API with the specified route
def show( route ):
	pcf_cc_api_url = get_cc_api_url()
	headers = build_headers()

	# call the PCF CC API, using the header with the bearer token
	res = requests.get(pcf_cc_api_url + route, headers=headers)
	if res.status_code != 200:
		res.raise_for_status()

	# convert the result to json
	js = res.json()
	resources = js['resources']

	print(resources)

# show_data queries the specified CC API with the specified route and displays all items in the returned resources list
def show_data( route ):
	pcf_cc_api_url = get_cc_api_url()
	headers = build_headers()

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

# get_data calls the CC API with the specified route, and then loops through the returned resources to build and return
# a list of the values of the specified entity_name in each returned record and (if requested) a list of the GUIDS for
# each returned record.
# If the requested entity_name is not present in any of the records returned from the CC API then an error is printed.
# The printing of this error can be supressed by setting the silent argument to True
# The entity_key_name specifies the value of the entity to be used as a key in the returned dictionary
# If the entity_key_name is specified, the attribute matching the entity_key_name is extracted from the entity record
# If the entity_key_name is the blank string, the key is extracted from the guid in the metadata record
def get_data( route, entity_name, entity_key_name=None, silent=None ):

	pcf_cc_api_url = get_cc_api_url()
	headers = build_headers()
	CERTIFICATE_BUNDLE = get_config_value('CERTIFICATE_BUNDLE')

	result = {}
	done = False

	while not done:
		# call the PCF CC API, using the header with the bearer token
		res = requests.get(pcf_cc_api_url + route, headers=headers, verify=CERTIFICATE_BUNDLE)
		if res.status_code != 200:
			res.raise_for_status()

		# convert the result to json, and grab the resources
		js = res.json()
		resources = js['resources']

		# loop through the items in the resources list
		for r in resources:
			# extract the entity key
			if entity_key_name is not None:
				entity_key = r['entity'][entity_key_name]
			else:
				entity_key = r['metadata']['guid']
			if entity_key != 'undefined':
				if entity_name in r['entity']:
					entity_value = r['entity'][entity_name]
					result[entity_key] = entity_value
				elif silent:
					result[entity_key] = 'unknown'
				else: # Didn't find the entity name, and silent is false
					print("Could not find " + entity_name + " in entity:")
					print(r['entity'])
			else:
				if entity_key_name is not None:
					print('Could not find attribute ' + entity_key_name + ' in record:')
				else:
					print('Could not find guid attribute in metadata for record:')
				print(r)
				exit()

		# If there is no next url then we are done
		next_url = js['next_url']
		if next_url == None:
			done = True
		else: # else use the next url for the route and do it again
			route = next_url

	return result

def get_items( route ):

	pcf_cc_api_url = get_cc_api_url()
	headers = build_headers()
	CERTIFICATE_BUNDLE = get_config_value('CERTIFICATE_BUNDLE')
	item_list = []
	done = False
	while not done:
		# call the PCF CC API, using the header with the bearer token
		res = requests.get(pcf_cc_api_url + route, headers=headers, verify=CERTIFICATE_BUNDLE)
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

def build_dict( route, entity_name ):

	pcf_cc_api_url = get_cc_api_url()
	headers = build_headers()
	CERTIFICATE_BUNDLE = get_config_value('CERTIFICATE_BUNDLE')
#	print('*' + CERTIFICATE_BUNDLE + '*')
	d = {}
	done = False
	while not done:
		# call the PCF CC API, using the header with the bearer token
		res = requests.get(pcf_cc_api_url + route, headers=headers, verify=CERTIFICATE_BUNDLE)
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

def build_dict_list( route, key_entity_name, value_entity_name ):

	pcf_cc_api_url = get_cc_api_url()
	headers = build_headers()
	CERTIFICATE_BUNDLE = get_config_value('CERTIFICATE_BUNDLE')
	d = {} # d is the dictionary that will be returned
	done = False
	while not done:
		# call the PCF CC API, using the header with the bearer token
		res = requests.get(pcf_cc_api_url + route, headers=headers, verify=CERTIFICATE_BUNDLE)
		if res.status_code != 200:
			res.raise_for_status()

		# convert the result to json
		js = res.json()

		resources = js['resources']
		# loop through the items in the resources list
		for r in resources:
			guid = r['metadata']['guid']
			if key_entity_name in r['entity']:
				key = r['entity'][key_entity_name]
				if value_entity_name in r['entity']:
					value = r['entity'][value_entity_name]
					if key in d:
						d[key].append(value)
					else:
						d[key] = [value]
				else:
					print("Could not find " + value_entity_name + " in:")
					print(r['entity'])
			else:
				print("Could not find " + key_entity_name + " in:")
				print(r['entity'])

		# If there is no next url then we are done
		next_url = js['next_url']
		if next_url == None:
			done = True
		else: # else use the next url for the route and do it again
			route = next_url

	return d
