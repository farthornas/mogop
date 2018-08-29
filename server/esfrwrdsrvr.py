#from twisted.protocols.basic import LineReceiver
from pprint import pprint
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import Factory
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet.defer import inlineCallbacks, returnValue, ensureDeferred, setDebugging
from twisted.logger import Logger
from txes2 import ElasticSearch
from txes2.exceptions import NoServerAvailable
from ast import literal_eval
import json
import time
import datetime
setDebugging(True)

log = Logger()

PLANT_IDEALS = 'plant_ideals'
PLANT_READING = 'plant_reading'
DATA_TYPE = 'type'
SPECIES = 'species'
DEVIATION_FROM = 'deviation_{}'
SENS_DATA = 's_'
MIN = '_min'
MAX = '_max'
TIMESTAMP = 'tstamp'
SENDERIP = 'sender_ip'
INDEX_IDEALS = 'idealstest'

#Ideals query should only return latest entry for the queried species

class Forward2Es(Protocol):

    def __init__(self):
        self.elastic = Elastic()

    def connectionMade(self):
        self.transport.write('{"message":"Welcome to Mogop Server","status":1}')

    def dataReceived(self, received_data):
        self.transport.write("Data is being handled\n")
        print("Data received")
        received_data = literal_eval(received_data)
        print("Data type is:{}".format(received_data['type']))
        t = timestamp()
        if 'hostname' not in received_data:
            received_data = add_key_val(received_data, SENDERIP, self.transport.getPeer().host)
        if PLANT_READING in received_data['type']:
            sens_data = sens_read_list(received_data)
            ideals_query = self.elastic.query_plant_ideals(received_data)
            ideals = ideals_query.addCallback(ideals_list)
            diff = ideals.addCallback(compute_diff, sens_data)
            updated_reading = diff.addCallback(add_dict, received_data)
            updated_reading.addCallback(self.elastic.index_data)
        if PLANT_IDEALS in received_data['type']:
            print("Ideals about to be indexed")
            received_data = self.elastic.add_key_val(received_data, TIMESTAMPIDEALS, t)
            p = self.elastic.index_data(received_data, index=INDEX_IDEALS)
            p.addErrback(lambda err: err.printTraceback())

        self.transport.write("Received data\n")

def sens_read_list(raw_data):
    """Return list of sensor values from incomming data"""
    sens_data = {}
    for data, value in raw_data.items():
        if SENS_DATA in data:
            sens_data.update({data:value})
    return sens_data

def ideals_list(ideals_entry):
    """return list of min_ideal/max_ideal for a species"""
    ideals = {}
    source = filter_source(ideals_entry)
    for ideal, estimate in source.items():
        if MIN in ideal or MAX in ideal:
            ideals.update({ideal:estimate})
    return ideals

def filter_source(i):
    """Return only ideals  from query result if there is any"""
    if i['hits']['total'] > 0:
        print("Plant ideals found")
        hits =  i['hits']['hits'][0]['_source']#ideals assuming only one entry
        return hits
    else:
        return None

def compute_diff(ideals, sens_read):
    """Method used to calculate difference between ideals and sensor
    values.
    Returns a dictionary with difference from ideal where ideals and
    reading found"""
    diff = {}
    print("Ideals: {}".format(ideals))
    print("Readings: {}".format(sens_read))
    for reading, value in sens_read.items():
        for ideal, estimate in ideals.items():
            if reading.strip() != (SPECIES or DATA_TYPE) and ideal.strip() != (SPECIES or DATA_TYPE):
                if ideal == reading: #Ideal without max and min value
                    deviation = (-1)*(int(estimate) - int(value))
                    d = {DEVIATION_FROM.format(ideal):deviation}
                    diff.update(d)
                if MIN in ideal: #Ideal with min value
                    lim_min_ideal = ideal.split(MIN)[0]
                    if lim_min_ideal in reading:
                        deviation = int(value) - int(estimate)
                        d = {DEVIATION_FROM.format(ideal):deviation}
                        diff.update(d)
                if MAX in ideal: #Ideal with max value
                    lim_max_ideal = ideal.split(MAX)[0]
                    if lim_max_ideal == reading:
                        deviation = int(value) - int(estimate)
                        d = {DEVIATION_FROM.format(ideal):deviation}
                        diff.update(d)
    print('Returned Diff:{}'.format(diff))
    return diff


class Elastic(object):
    #DOC TYPES
    def __init__(self, host='127.0.0.1', port='9200', index='sandbox', doc_type='test'):
        self.host = host
        self.port = port
        self.index = index
        self.doc_type = doc_type
        self.es = ElasticSearch('{}:{}'.format(host,port) )

    @inlineCallbacks
    def index_data(self, data, index=None):
        print("Indexing")
        tstamp = timestamp()
        data = add_key_val(data, "tstamp", tstamp)
        if index is None:
            index = self.index
        yield self.es.index(data, doc_type=self.doc_type, index=index)
        print("Data indexed")

    @inlineCallbacks
    def query_plant_ideals(self, data):
        species = data.get('species')

        query = {"sort":[{TIMESTAMP: {"order" : "desc"}}],
                 "size":1,
                 "query": {"match_phrase": {"species": {"query":species}}}}

        answer = yield self.es.search(query, indexes=INDEX_IDEALS)
        returnValue(answer)


def timestamp():
    timestamp = int (time.time()*1000)
    return timestamp

def print_results_received(results):
    print("Results Received START:")
    pprint(results)
    print("Results Received END")

def add_key_val(data, key, val):
    data[key] = val
    return data

def add_dict(data_update, data):
    updated = {}
    updated.update(data_update)
    updated.update(data)
    return updated


class Forward2EsFactory(Factory):
    def buildProtocol(self, addr):
        return Forward2Es()


if __name__ =='__main__':
    endpoint = TCP4ServerEndpoint(reactor, 1234)
    endpoint.listen(Forward2EsFactory())
    reactor.run()
