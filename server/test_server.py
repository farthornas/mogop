from pprint import pprint

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue

from txes2 import ElasticSearch

TIMESTAMPIDEALS = 'tstamp'
IDEALS_QUERY = {"sort":[  {TIMESTAMPIDEALS: { "order" : "desc"}} ],
                "size":1,
                "query": {"match_phrase": {"species": {"query":"{}"}}}}

@inlineCallbacks
def example():

    index = 'idealstest'
    species = "palm2"
    es = ElasticSearch('127.0.0.1:9200')
    query = {"sort":[{TIMESTAMPIDEALS: {"order" : "desc"}}],
             "size":1,
             "query": {"match_phrase": {"species": {"query":species}}}}


    result = yield es.search(query, indexes=index)#index not recognised, indexes concidered in query
    returnValue(result)

@inlineCallbacks
def print_it(it):
    pprint(it)

if __name__ == "__main__":
    df = example()
    df.addCallback(print_it)
    df.addErrback(lambda err: err.printTraceback())
    df.addCallback(lambda _: reactor_stop())
    reactor.run()

