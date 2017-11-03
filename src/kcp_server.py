#coding=utf-8

import txkcp
import logging
from twisted.internet import protocol, reactor, defer

import config
import txkcp
import ikcp

class KcpOutgoing(protocol.Protocol):
    def __init__(self, peersock, defer):
        assert peersock
        logging.debug("kcp outgoing init")
        self.peersock = peersock
        self.peersock.peersock = self
        self.defer = defer

    def connectionMade(self):
        self.defer.callback(None)

    def connectionLost(self, reason):
        logging.debug("connection lost: %s" % reason)
        self.peersock.loseConnection()
        self.peersock.peersock = None
        self.peersock = None
        
    def dataReceived(self, buf):
        logging.debug("data received: %d" % len(buf))
        self.peersock.send(buf)

class ServerProtocol(txkcp.Protocol):
    mode=ikcp.FAST_MODE

    def startProtocol(self, defer):
        logging.debug("kcp server protocol is starting")
        protocol.ClientCreator(reactor, KcpOutgoing, self, defer)\
                .connectTCP(config.SERVER, config.SERVER_PORT)

    def dataReceived(self, data):
        self.peersock.transport.write(data)

class ServerProtocolFactory(txkcp.ProtocolFactory):
    protocol = ServerProtocol
