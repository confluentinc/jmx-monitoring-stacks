#!/usr/bin/env python

import requests
import json
import time
import pathlib
from elasticsearch import Elasticsearch
from urllib.parse import urlparse

jmxDashboardFilename = "jmx_dashboard.json"
# The index will automatically be created with a date extensions to create index per day and keep the clean up easier
#  You will still have to create a read the timestamp in millis ( createdDateTime ) in elastic & extract a date from it
elasticIndexName = "kafka-jmx-logs"
# I will whole heartily recommend not resolving below 30 seconds as the process needs to execute all the URL's in a
# loop and the Java process will need time to breath , not some other process asking for metrics every 5-10 seconds.
waitTimeInSeconds = 60

# the url for Elastic connection. No support for SSL yet. maybe some time soon , but need to get the code running first.
elasticURL = "http://elasticsearch:9200"
# this is the Kibana dashboard URL. This is needed for the initial index, visualization and dashboard setup.
kibanaURL = "http://kibana:5601"

# The list of endpoints to be farmed. The Structure is a Dictionary with the Server/Component type as the Key and
# Value is a list of JMX URL's that need to be farmed for those servers.
urllist = {"ZooKeeper": ["http://zookeeper:49900/jolokia/read/org.apache.ZooKeeperService:*"],
           "KafkaBroker": ["http://kafka1:49900/jolokia/read/kafka.*:*",
                           "http://kafka2:49900/jolokia/read/kafka.*:*"],
           "KafkaConnect": ["http://connect:49900/jolokia//read/kafka.*:*"]
           }
# TODO : In progress for implementation to add Alias name or alternate names instead of Hostnames for beautifying the dashboard
# aliasServerNames = [{"ZooKeeper1" : "http://localhost:49900"},
#                     {"KafkaBroker1" : "http://localhost:49910"},
#                     {"KafkaBroker2" : "http://localhost:49911"},
#                     {"KafkaConnect1" : "http://localhost:49920"}
#                     ]
#  This JMX URL fetcher is a common fetcher which will be run on all the Servers provided above. Dont worry about the
#  unique servers, the script figures it out and constructs the list accordingly.
defaultJMXFetch = ["/jolokia/read/java.lang:type=*"]
# Lambda function to fetch current time in millis when needed in an int format
current_milli_time = lambda: int(round(time.time() * 1000))

# This function call provides a dictionary of unique servers found in the urllist variable. More or less like a logical
# de-dupe process. The dictionary is reversed though - the Key is the Server URL and Value is the type of server it is.
def get_unique_server_list():
    # Setup some variables to work with.
    hostnames = []
    dictHostnamePairs = {}
    splitterValue = "____"
    # Iterate over data and sort out the details
    for serverType, serverList in urllist.items():
        for url in serverList:
            urlDetails = urlparse(url)
            hostnames.append(serverType + splitterValue + str(urlDetails.scheme + "://" + urlDetails.hostname + ":" + str(urlDetails.port)))
    # Dedupe in a single line ;) -- not so performant , but simpler
    hostnames = list(set(hostnames))
    #  this statement converts the de-duped list into a dict for sending as a response
    for item in hostnames:
        dictHostnamePairs[item.split(splitterValue)[1]] = item.split(splitterValue)[0]
    # print(dictHostnamePairs)
    return (dictHostnamePairs)


# TODO : In progress for implementation to add Alias name or alternate names instead of Hostnames for beautifying the dashboard
def get_alias_name_mapper():
    for item in get_unique_server_list():
        print( str(item)) #+ "   " + str(item.value))

# This function merges data received from get_unique_server_list() function and creates logical unique JMX URL's to hit.
def add_default_fetch_list_to_urlist(uniqueURLs , destinationURLList ):
    for key, value in destinationURLList.items():
        for filteredHostURL, fileteredHostType in {k: v for k, v in uniqueURLs.items() if v == key}.items():
            for defaultJMXFetchItem in defaultJMXFetch:
                value.append(str(filteredHostURL + defaultJMXFetchItem))
    # De-dupe URL list for all server types
    for i, j in destinationURLList.items():
        newValue = list(set(j))
        destinationURLList[i] = newValue
    return destinationURLList


#  this function iterates over all the urls provided in a list and get their output formatted in a JSON format
def get_data_from_jolokia(url):
    contents = requests.get(url).json()
    return json.loads(json.dumps(contents))['value']


# This function formats the JSON as per our needs and straightens out data from a dictionary format to a list format
# with double quotes on all string fields
#  It also injects some additional fields for easing the Dashboard creation
def get_structured_json_from_response(responseData, serverIdentifier, serverHostName):
    # Instantiate Empty Lists for storing data
    returnDataSet = []
    formattedJSONDataPairs = []
    currDateTime = current_milli_time()
    for key, value in responseData.items():
        formatterDataKVPairStrings = []
        if ":" in key:
            formattedDataHeader = str(key.split(":")[0])
            formatterDataKVPairStrings = key.split(":")[1].split(",")
            value["injectedBeanName"] = formattedDataHeader
            value["createdDateTime"] = currDateTime
            value["injectedServerType"] = serverIdentifier
            value["injectedHostName"] = serverHostName
        else:
            responseData["createdDateTime"] = currDateTime
            responseData["injectedServerType"] = serverIdentifier
            responseData["injectedHostName"] = serverHostName
            returnDataSet.append(json.dumps(responseData))
            return returnDataSet
        for item in range(len(formatterDataKVPairStrings)):
            dataKVPair = formatterDataKVPairStrings[item].split("=")
            value[dataKVPair[0]] = dataKVPair[1]
        returnDataSet.append(json.dumps(value))
    return returnDataSet


# Creates a file with data to be inserted using ES API.
# The file format is strictly adhering to ES bulk insert and was designed to insert in bulk by default.
def write_data_to_file(fileName, jsonDict):
    with open(fileName, "w") as file:
        firstRunflag = True
        for item in jsonDict:
            if firstRunflag:
                file.write("{\"index\":{\"_type\": \"doc\"}}")
                firstRunflag = False
            else:
                file.write("\n{\"index\":{\"_type\": \"doc\"}}")
            file.write("\n" + str(item))


#  Used to clean up the files created per iteration to keep everything neat and clean
def clean_up_file(fileName):
    path = pathlib.Path(fileName)
    path.unlink()

#
def create_elastic_index_template():
    # Create first set of headers for inserting the templates
    headers = {
        'Content-Type': 'application/json',
    }
    # setup the body for inserting the templates
    data = '{"template": "' + elasticIndexName + '-*","mappings": {"default": {"properties": {"createdDateTime": {"type": "date"}}}}}'
    # Insert the template into Elastic for datatime formatting
    response = requests.put(elasticURL + '/_template/' + elasticIndexName + '_template', headers=headers, data=data)
    # Setup the headers for inserting index
    headers = {
        'Content-Type': 'application/json',
        'kbn-version': '5.5.2'
    }
    # Create the index pattern for Kibana
    indexCreation = '{"title": "' + elasticIndexName + '-*","notExpandable":true, "timeFieldName": "createdDateTime"}'
    #  insert the index pattern for Kibana
    response = requests.put( kibanaURL + '/es_admin/.kibana/index-pattern/' + elasticIndexName + '-*/_create', headers=headers, data=indexCreation)
    # Parse all the objects in the Dashboard & Visualization file as Kibana 5.5.2 does not have a bulk API for insert.
    # Setup the headers for inserting objects into Kibana
    headers = {
        'Content-Type': 'application/json',
        'kbn-version': '5.5.2',
        'kbn-xsrf' : 'true'
    }
    with open(jmxDashboardFilename , "r") as file:
        fileContents = json.load(file)
        for objectlistValues in fileContents:
            response = requests.put(kibanaURL + '/es_admin/.kibana/' + str(objectlistValues["_type"]) + "/" + str(objectlistValues["_id"]), headers=headers, json=objectlistValues["_source"])


# Read data from the file and bulk ingest into a specific Elastic index
def call_elastic_bulk(url, fileName):
    es_client = Elasticsearch([elasticURL])
    body = []
    with open(fileName, "r") as file:
        body = file.read().splitlines()
    currIndexName = elasticIndexName + "-" + time.strftime("%Y-%m-%d")
    es_client.bulk(body=body, index=currIndexName)


# Code begins here.
urllist = add_default_fetch_list_to_urlist(get_unique_server_list(), urllist)
create_elastic_index_template()

runCode = True
if runCode:
    while (True):
        print(" Bulk ingest into Elastic Started at time" + time.strftime("%Y-%m-%d %H:%M:%S"))
        for serverType, serverList in urllist.items():
            for url in serverList:
                urlDetails = urlparse(url)
                serverHostName = str(urlDetails.hostname + ":" + str(urlDetails.port))
                contents = get_data_from_jolokia(url)
                print("Data for URL: " + url + " is in format " + str(type(contents)))
                jsonDataString = get_structured_json_from_response(contents, serverType, serverHostName)
                currFileName = str(current_milli_time()) + "_data.json"
                write_data_to_file(currFileName, jsonDataString)
                call_elastic_bulk(elasticURL, currFileName)
                clean_up_file(currFileName)
        print(" Bulk ingest into Elastic Complete at time" + time.strftime("%Y-%m-%d %H:%M:%S"))
        print("=" * 120)
        time.sleep(waitTimeInSeconds)

