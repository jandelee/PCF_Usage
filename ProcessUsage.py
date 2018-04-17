#! python

import sys, subprocess
# ProcessUsage.py takes as input a text file that was generated from executing the cf usage-report command,
# and generates two new files that summarize the org and space usage based on that input text file
# The org data can then be loaded into ES using the LoadUsageDataToES app

# Process the -generate option if it exists
generate = False
if len(sys.argv)>1:
	if sys.argv[1] == '-generate':
		generate = True
		del sys.argv[1]

# make sure we have exactly 2 arguments
if len(sys.argv) == 2:
	filename = sys.argv[1]
else:
	print('Usage:', str(sys.argv[0]), '[-generate] <usage_file>')
	print('   where usage_file is the file to be processed that was generated from "cf usage-report"')
	print('   if the -generate option is specified, the usage report will be generated and placed in a file with the name <usage_file> before the script processing occurs')
	exit()

# If the generate option was specified
if generate:
	# Generate the usage report
	CP = subprocess.run(["cf", "usage-report"], stdout=subprocess.PIPE)
	if CP.returncode != 0:
		print("Error occurred executing 'cf usage-report' command")
		exit()
	result = CP.stdout.strip() # get the results of running the command and strip off the trailing newline
	result = result.decode() # convert to string; result consists of multiple lines
	lines = result.split('\n')

	# write out the usage file
	with open(filename, "w") as usage_file:
		for line in lines:
			print(line, file=usage_file)

# open the text file that contains the usage report
with open(filename, 'rU') as usage_file:

	# If the filename ends with .txt
	if filename[-4:] == ".txt":
		# Remove the .txt from the filename
		filename = filename[:-4]

	# construct the org and space filename
	org_filename = filename + "org.csv"
	space_filename = filename + "space.csv"

	# open the org and space files for output
	with open(org_filename, 'w') as org_file, open(space_filename, 'w') as space_file:

		# let the user know the names of these files
		print("Org information placed in " + org_filename)
		print("Space information placed in " + space_filename)

		show_spaces = 1
		org = ""
		total_org_apps = 0
		total_org_stopped_apps = 0
		total_org_instances = 0
		total_org_stopped_instances = 0
		total_org_usage = 0
		print("Org,Org_Usage,Org_Quota,Spaces,Running_Apps,Stopped_Apps,Total_Apps,Running_Instances,Stopped_Instances,Total_Instances", file=org_file)
		print("Org,Space_Usage,,Spaces,Running_Apps,Stopped_Apps,Total_Apps,Running_Instances,Stopped_Instances,Total_Instances", file=space_file)

		# For each line in the usage file
		for line in usage_file:

			line = line.strip() # remove all leading and trailing whitespace - in particular, tabs in front of "Space", "apps", and "instances" lines
			words = line.split()

			# If the first word on the current line of the usage file is Org
			if words[0] == 'Org':

				# If there is a previous org in the buffer
				if org != "":

					# write it to the org file
					print("%s,%d,%d,%s," % (org,org_usage,org_quota,spaces), file=org_file, end="")
					print("%d,%d,%d," % (org_apps,org_stopped_apps,(org_apps + org_stopped_apps)), file=org_file, end="")
					print("%d,%d,%d" % (org_instances,org_stopped_instances,(org_instances+org_stopped_instances)), file=org_file)
					total_org_apps = total_org_apps + org_apps
					total_org_stopped_apps = total_org_stopped_apps + org_stopped_apps
					total_org_instances = total_org_instances + org_instances
					total_org_stopped_instances = total_org_stopped_instances + org_stopped_instances
					total_org_usage = total_org_usage + org_usage

				# Extract the org name
				org = line[4:line.find("is consuming")-1]

				# Move past the org name in the current line and re-split the line
				line = line[line.find("is consuming"):]
				words = line.split()

				# Extract the memory usage (in MB) and quota (in MB) for this org
				org_usage = int(words[2])
				org_quota = int(words[5])

				# Reset counters for this org; these will be incremented appropriately as the space information is read in on subsequent lines
				org_apps = 0
				org_instances = 0
				org_stopped_apps = 0
				org_stopped_instances = 0
				spaces = 0

			# Else if the first word on the current line of the usage file is Space
			elif words[0] == 'Space':

				# Extract the space name
				space = line[6:line.find("is consuming")-1]

				# Move past the space name in the current line and re-split the line
				line = line[line.find("is consuming"):]
				words = line.split()

				# Extract the memory usage (in MB) for this space
				space_usage = int(words[2])

				# Increment the space counter for this org
				spaces = spaces + 1
				print("%s,%d,,%s" % (org,space_usage,space), file=space_file, end="")

			# Else if the first word on the current line of the usage file is You
			elif words[0] == 'You':

				# We should have an org in the buffer, so print it out
				print("%s,%d,%d,%s," % (org,org_usage,org_quota,spaces), file=org_file, end="")
				print("%d,%d,%d," % (org_apps,org_stopped_apps,(org_apps + org_stopped_apps)), file=org_file, end="")
				print("%d,%d,%d" % (org_instances,org_stopped_instances,(org_instances+org_stopped_instances)), file=org_file)

				# Calculate totals for all orgs
				total_org_apps = total_org_apps + org_apps
				total_org_stopped_apps = total_org_stopped_apps + org_stopped_apps
				total_org_instances = total_org_instances + org_instances
				total_org_stopped_instances = total_org_stopped_instances + org_stopped_instances
				total_org_usage = total_org_usage + org_usage
				# Print out the totals for all orgs
				print("Total for all orgs,%d,,,%d,%d,%d," % (total_org_usage, total_org_apps, total_org_stopped_apps, (total_org_apps+total_org_stopped_apps)), file=org_file, end="")
				print("%d,%d,%d" % (total_org_instances,total_org_stopped_instances, (total_org_instances+total_org_stopped_instances)), file=org_file)

				# Extract the app, org, and instance count from the usage file
				apps = int(words[3])
				orgs = int(words[6])
				instances = int(words[12])

				# Print out these counts so that they can be compared to the results calculated by this script if desired
				print("Orgs, apps, and instances from the usage file:")
				print("%d,%d,%d" % (orgs,apps,instances))
				exit() # we're done

			# Else if the second word on the current line of the usage file is apps:
			elif words[1] == 'apps:':

				# Extract the count of running and stopped apps for this space
				running_apps = int(words[2])
				stopped_apps = int(words[4])

				# print out the running apps, stopped apps and total apps for this space
				print(",%d,%d,%d" % (running_apps,stopped_apps,(running_apps + stopped_apps)), file=space_file, end="")

				# Increment counters for the org
				org_apps = org_apps + running_apps
				org_stopped_apps = org_stopped_apps + stopped_apps

			# Else if the second word on the current line of the usage file is instances:
			elif words[1] == 'instances:':

				# Extract the running and stopped instances for this space
				running_instances = int(words[2])
				stopped_instances = int(words[4])
				print(",%d,%d,%d" % (running_instances,stopped_instances,(running_instances + stopped_instances)), file=space_file)
				org_instances = org_instances + running_instances
				org_stopped_instances = org_stopped_instances + stopped_instances

			# Else the current line is not in a format that we expected
			else:

				# We found a line that did not have a format we expected, so print an error
				print("Found invalid line:")
				print(line)
