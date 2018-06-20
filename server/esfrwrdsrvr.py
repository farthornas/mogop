#from twisted.protocols.basic import LineReceiver
from pprint import pprint
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import Factory
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet.defer import inlineCallbacks, returnValue, ensureDeferred
from twisted.logger import Logger
from txes2 import ElasticSearch
from txes2.exceptions import NoServerAvailable
from ast import literal_eval
import json
import time
import datetime

log = Logger()

PLANT_IDEALS = 'plant_ideals'
PLANT_READING = 'plant_reading'
DATA_TYPE = 'type'
SPECIES = 'species'
DEVIATION_FROM = 'deviation_{}'
MIN = '_min'
MAX = '_max'
TIMESTAMP = 'timestamp'
SENDERIP = 'sender_ip'

class Forward2Es(Protocol):

    def __init__(self):
        self.elastic = Elastic()
        #servers = self.elastic.servers
        #if self.elastic.servers() == []:

    def connectionMade(self):
        self.transport.write('{"message":"Welcome to Mogop Server","status":1}')

    def dataReceived(self, received_data):
        self.transport.write("Data is being handled\n")
        print("Data received")
        received_data = literal_eval(received_data)
        print("Data type is:{}".format(received_data['type']))
        t = self.elastic.esTimestamp()
        if 'hostname' not in received_data:
            received_data = self.elastic.add_key_val(received_data, SENDERIP, self.transport.getPeer().host)
        if PLANT_READING in received_data['type']:
            received_data = self.elastic.add_key_val(received_data, TIMESTAMP, t)
            ideals_query = self.elastic.query_plant_ideals(received_data)
            ideals = ideals_query.addCallback(self.filter_ideals)
            ideals.addErrback(lambda err: err.printTraceback())
            diff = ideals.addCallback(self.compute_diff, received_data)
            updated_reading = diff.addCallback(self.elastic.add_dict, received_data)
            updated_reading.addCallback(self.elastic.index_data)
            diff.addErrback(lambda err: err.printTraceback())
        if PLANT_IDEALS in received_data['type']:
            print("Ideals about to be indexed")
            received_data = self.elastic.add_key_val(received_data, 'tstamp', t)
            p = self.elastic.index_data(received_data, index='idealstest')
            p.addErrback(lambda err: err.printTraceback())

        self.transport.write("Received data\n")
        print("trying to write back")
    

    def filter_ideals(self, i):
        """Return only ideals  from query result if there is any"""
        
        if i['hits']['total'] > 0:
            print("Plant ideals found")
            hits =  i['hits']['hits'][0]['_source']#ideals assuming only one entry
            print(hits)
            return hits
        else:
            return None

    def compute_diff(self, ideals, sens_read):
        """Method used to calculate difference between ideals and sensor
        values.
        Returns a dictionary with difference from ideal where ideals and
        reading found"""
        diff = {}
        for reading, value in sens_read.items():
            for ideal, estimate in ideals.items():
                if reading.strip() != (SPECIES or DATA_TYPE) and ideal.strip() != (SPECIES or DATA_TYPE):
                    print("Inside for for if")
                    if ideal == reading: #Ideal without max and min value
                        print("Inside for for if if equal")
                        deviation = (-1)*(int(estimate) - int(value))
                        d = {DEVIATION_FROM.format(ideal):deviation}
                        diff.update(d)
                    if MIN in ideal: #Ideal with min value
                        print("Inside for for if if min")
                        lim_min_ideal = ideal.split(MIN)[0]
                        if lim_min_ideal in reading:
                            deviation = int(value) - int(estimate)
                            d = {DEVIATION_FROM.format(ideal):deviation}
                            diff.update(d)
                    if MAX in ideal: #Ideal with max value
                        print("Inside for for if if max")
                        lim_max_ideal = ideal.split(MAX)[0]
                        print(lim_max_ideal)
                        if lim_max_ideal == reading:
                            deviation = int(value) - int(estimate)
                            d = {DEVIATION_FROM.format(ideal):deviation}
                            diff.update(d)
        return diff

    def printer(self, i):
        print('printing results')
        print(i)

class Elastic(object):
    #DOC TYPES
    def __init__(self, host='127.0.0.1', port='9200', index='sandbox', doc_type='test'):
        self.host = host
        self.port = port
        self.index = index
        self.doc_type = doc_type
        self.es = ElasticSearch('{}:{}'.format(host,port) )

    def esTimestamp(self):
        timestamp = int (time.time()*1000)
        return timestamp

    @inlineCallbacks
    def index_data(self, data, index=None):
        if index is None:
            index = self.index
        i = self.es.index(data, doc_type=self.doc_type, index=index)
        print("Data indexed")
        yield i

    #@inlineCallbacks
    def query_plant_ideals(self, data):
        species = data.get('species')
        print("\nQuery for plant:".format(species))
        query = {'query': {'match': {'species': { 'query': species, 'type': 'phrase'}}}}
        returned = self.es.search(query, doc_type=PLANT_IDEALS, index='test3')
        return returned

    def print_results_received(results):
        print('Result Received: {}'.format(results))
    
    def add_key_val(self, data, key, val):
        data[key] = val
        return data

    def add_dict(self, data_update, data):
        updated = {}
        updated.update(data_update)
        updated.update(data)
        return updated


class Forward2EsFactory(Factory):
    def buildProtocol(self, addr):
        return Forward2Es()


if __name__ =='__main__':
    #fe = Forward2Es()
    endpoint = TCP4ServerEndpoint(reactor, 1234)
    endpoint.listen(Forward2EsFactory())
    #fe.addErrback(lambda err: err.printTraceback())
    reactor.run()
    print("reactor running")
