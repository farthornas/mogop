import json
from pprint import pprint
import time
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks,returnValue, ensureDeferred, setDebugging
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet.protocol import Factory
from twisted.internet.protocol import Protocol
from twisted.logger import Logger

class ForwardData(Protocol):

    def connectionMade(self):
        print("Connection made...")
        self.transport.write('{"message":"Welcome to Mogop Server", "status":1}')

    def dataReceived(self, received_data):
        self.transport.write("Data is being handled\n")
        print(received_data)
        self.transport.loseConnection()

class ForwardDataFactory(Factory):
    def buildProtocol(self, addr):
        return ForwardData()

endpoint = TCP4ServerEndpoint(reactor, 8007)
endpoint.listen(ForwardDataFactory())
print("Starting Server")
reactor.run()
