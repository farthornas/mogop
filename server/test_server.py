from pprint import pprint

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue

from txes2 import ElasticSearch

@inlineCallbacks
def example():

    index = 'idealstest'
    doc_type = 'test'
    es = ElasticSearch('127.0.0.1:9200')

    query = {"size":1,"sort":[  {"tstamp": { "order" : "desc" }} ],"query": {"match_phrase": {"species": {"query":"palm2"}}}}
    r = yield es.search(index = index, doc_type = doc_type,query = query)#Index does not seem to be concidered in query
    #by txes2, this causes elasticsearch to throw exception on idicies which does not have a field called tstamp.
    returnValue(r)

@inlineCallbacks
def print_it(it):
    pprint(it)

if __name__ == "__main__":
    df = example()
    df.addCallback(print_it)
    df.addErrback(lambda err: err.printTraceback())
    df.addCallback(lambda _: reactor_stop())
    reactor.run()

