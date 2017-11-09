#coding=utf-8

import txkcp
import logging
from twisted.internet import protocol, reactor, defer

import config
import txkcp
import random

class ClientOutgoing(txkcp.Protocol):
    def __init__(self, addr, peer, conv):
        self.addr = addr
        self.peer = peer
        self.peer.outgoing = self

        txkcp.Protocol.__init__(self, self.addr, conv)

    def dataReceived(self, data):
        logging.debug("data received: %d" % len(data))
        self.peer.transport.write(data)

class LocalProxyProtocol(protocol.Protocol):
    def connectionMade(self):
        self.srv_addr = (config.SERVER_KCP_ADDR, config.SERVER_KCP_PORT)
        conv = random.randint(10000, 30000)
        reactor.listenUDP(0, ClientOutgoing(self.srv_addr, self, conv))

    def dataReceived(self, data):
        self.outgoing.send(data)

    def connctionLost(self, reason):
        logging.error("connection lost for reason: %s" % reason)

class LocalProxyProtocolFactory(protocol.ServerFactory):
    protocol = LocalProxyProtocol
