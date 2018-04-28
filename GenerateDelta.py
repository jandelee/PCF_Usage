import sys

# make sure we have exactly 4 arguments
if len(sys.argv) == 4:
   original_filename = sys.argv[1]
   revised_filename = sys.argv[2]
   field_to_compare = int(sys.argv[3])
else:
   print('Usage:', str(sys.argv[0]), ' <original_filename> <revised_filename> <field_to_compare>')
   print('   where original_filename is the filename of the original (baseline) CSV file to be compared')
   print('   where revised_filename is the filename of the new (revised) CSV file to be compared')
   print('   where field_to_compare is the number of the field to be compared between the original and revised files')
   print('   This produces a resulting CSV that consists of the revised file with the comparison at the end of each line')
   exit()

with open(original_filename, "rU") as original_file:
   line = original_file.readline() # Assume this is a heading line
   baseline = {}
   for line in original_file:
      words = line.split(',')
      baseline[words[0]] = words[field_to_compare]

with open(revised_filename, "rU") as revised_file:
   line = revised_file.readline() # Assume this is a heading line
   print(line.strip() + ',Delta')
   for line in revised_file:
      words = line.split(',')
      key = words[0]
      if key in baseline:
         delta = int(words[field_to_compare]) - int(baseline[key])
      else:
         delta = words[field_to_compare]
      print(line.strip() + ',' + str(delta))
