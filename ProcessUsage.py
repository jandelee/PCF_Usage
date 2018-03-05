import sys
# ProcessUsage.py takes as input a text file that was generated from executing the cf usage-report command,
# and generates two new files that summarize the org and space usage based on that input text file
# The org data can then be loaded into ES using the LoadUsageDataToES app

# make sure we have exactly 1 argument 
if len(sys.argv) != 2:
	print('Usage:', str(sys.argv[0]), 'usage_file')
	print('   where usage_file is the file to be processed that was generated from "cf usage-report"')
	exit()
else:
	filename = sys.argv[1]

with open(filename, 'rU') as usage_file:

	# construct the org and space filename
	org_filename = filename + "org.csv"
	space_filename = filename + "space.csv"

	# open the org and space files for output
	with open(org_filename, 'w') as org_file, open(space_filename, 'w') as space_file:
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
		for line in usage_file:
			#print("line=" + line)
			line = line.strip() # remove all leading and trailing whitespace - in particular, tabs in front of "Space", "apps", and "instances" lines
			words = line.split()
			#print("words[0] = " + words[0])
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
				org = line[4:line.find("is consuming")-1]
				line = line[line.find("is consuming"):]
				words = line.split()
				org_usage = int(words[2])
				org_quota = int(words[5])
				org_apps = 0
				org_instances = 0
				org_stopped_apps = 0
				org_stopped_instances = 0
				spaces = 0
			elif words[0] == 'Space':
				space = line[6:line.find("is consuming")-1]
				line = line[line.find("is consuming"):]
				words = line.split()
				space_usage = int(words[2])
				spaces = spaces + 1
				#if show_spaces:
				print("%s,%d,,%s" % (org,space_usage,space), file=space_file, end="")
			elif words[0] == 'You':
				# We should have an org in the buffer, so print it out
				print("%s,%d,%d,%s," % (org,org_usage,org_quota,spaces), file=org_file, end="")
				print("%d,%d,%d," % (org_apps,org_stopped_apps,(org_apps + org_stopped_apps)), file=org_file, end="")
				print("%d,%d,%d" % (org_instances,org_stopped_instances,(org_instances+org_stopped_instances)), file=org_file)
				total_org_apps = total_org_apps + org_apps
				total_org_stopped_apps = total_org_stopped_apps + org_stopped_apps
				total_org_instances = total_org_instances + org_instances
				total_org_stopped_instances = total_org_stopped_instances + org_stopped_instances
				total_org_usage = total_org_usage + org_usage
				print("Total,%d,,,%d,%d,%d," % (total_org_usage, total_org_apps, total_org_stopped_apps, (total_org_apps+total_org_stopped_apps)), file=org_file, end="")
				print("%d,%d,%d" % (total_org_instances,total_org_stopped_instances, (total_org_instances+total_org_stopped_instances)), file=org_file)
				apps = int(words[3])
				orgs = int(words[6])
				instances = int(words[12])
				print("%d,%d,%d" % (orgs,apps,instances))
				exit()
			elif words[1] == 'apps:':
				running_apps = int(words[2])
				stopped_apps = int(words[4])
				#if ($show_spaces) {
				print(",%d,%d,%d" % (running_apps,stopped_apps,(running_apps + stopped_apps)), file=space_file, end="")
				#}
				org_apps = org_apps + running_apps
				org_stopped_apps = org_stopped_apps + stopped_apps
			elif words[1] == 'instances:':
				running_instances = int(words[2])
				stopped_instances = int(words[4])
				#if ($show_spaces) {
				print(",%d,%d,%d" % (running_instances,stopped_instances,(running_instances + stopped_instances)), file=space_file)
				#}
				org_instances = org_instances + running_instances
				org_stopped_instances = org_stopped_instances + stopped_instances
			else:
				print("Found invalid line:")
				print(line)
