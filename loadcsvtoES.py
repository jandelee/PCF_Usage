# loadcsvtoES.py loads the provided csv file into ElasticSearch using the bulk API

import sys

# make sure we have exactly 2 arguments (first is the name of the python script, second is the name of the file to load into ES
if len(sys.argv) != 2:
	print('Usage:', str(sys.argv[0]), 'csv_file')
	print('   where csv_file is the file to be loaded into ElasticSearch')
	exit()
else:
	filename = sys.argv[1]

ES_HOST = {
    "host" : "localhost", 
    "port" : 9200
}

INDEX_NAME = 'pcf_usage'
TYPE_NAME = 'org'

import csv
import urllib2

from elasticsearch import Elasticsearch

with open(filename) as csvfile:
	csvreader = csv.reader(csvfile, delimiter=',')
	header = csvreader.next()
	header = [item.lower() for item in header]

	bulk_data = []

	for row in csvreader:
		data_dict = {}
		for i in range(len(row)):
			data_dict[header[i]] = row[i]
		op_dict = {
			"index": {
				"_index": INDEX_NAME, 
				"_type": TYPE_NAME, 
			}
		}
		bulk_data.append(op_dict)
		bulk_data.append(data_dict)

# create ES client, create index
es = Elasticsearch(hosts = [ES_HOST])

if es.indices.exists(INDEX_NAME):
	print("deleting '%s' index..." % (INDEX_NAME))
	res = es.indices.delete(index = INDEX_NAME)
	print(" response: '%s'" % (res))

request_body = {
	"settings" : {
		"number_of_shards": 1,
		"number_of_replicas": 0
	}
}

print("creating '%s' index..." % (INDEX_NAME))
res = es.indices.create(index = INDEX_NAME, body = request_body)
print(" response: '%s'" % (res))

# bulk index the data
print("bulk indexing...")
res = es.bulk(index = INDEX_NAME, body = bulk_data, refresh = True)
#print(" response: '%s'" % (res))

# sanity check
print("searching...")
res = es.search(index = INDEX_NAME, size=2, body={"query": {"match_all": {}}})
print(" response: '%s'" % (res))

print("results:")
for hit in res['hits']['hits']:
	print(hit["_source"])