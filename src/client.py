#coding=utf-8

import logging
from twisted.internet import defer, protocol, reactor, error

import config
from protocol import MelkwegClientProtocol
from packet_factory import PacketFactory

class MelkwegLocalProxyProtocol(protocol.Protocol):
    def __init__(self, addr, port, outgoing):
        self.addr = addr
        self.port = port
        self.outgoing = outgoing

        self.outgoing.d[self.port] = self

    def connectionMade(self):
        logging.debug("proxy connection made")

    def dataReceived(self, buf):
        logging.debug("outgoing buf size: %s" % len(buf))
        if self.outgoing.transport:
            self.outgoing.write(PacketFactory.create_data_packet(self.port, buf))
        else:
            self.transport.loseConnection()

    def connectionLost(self, reason):
        if reason.check(error.ConnectionDone):
            self.outgoing.write(PacketFactory.create_fin_packet(self.port))
        else:
            self.outgoing.write(PacketFactory.create_rst_packet(self.port))
        if self.port in self.outgoing.d:
            del self.outgoing.d[self.port]

class MelkwegClientProtocolFactory(protocol.ReconnectingClientFactory):
    protocol = MelkwegClientProtocol
    initialDelay = 3
    maxDelay = 10
    outgoing = None

    def __init__(self):
        MelkwegClientProtocolFactory.outgoing = MelkwegClientProtocol()

    def buildProtocol(self, addr):
        if self.outgoing == None:
            MelkwegClientProtocolFactory.outgoing = MelkwegClientProtocol()
        return self.outgoing

    def clientConnectionFailed(self, connector, reason):
        logging.error("connection failed: %s" % reason)
        MelkwegClientProtocolFactory.outgoing = MelkwegClientProtocol()
        protocol.ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

    def clientConnectionLost(self, connector, reason):
        logging.error("connection lost: %s" % reason)
        MelkwegClientProtocolFactory.outgoing = MelkwegClientProtocol()
        protocol.ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

class MelkwegLocalProxyFactory(protocol.Factory):
    protocol = MelkwegLocalProxyProtocol

    def __init__(self):
        reactor.connectTCP(
                config.SERVER, config.SERVER_PORT, MelkwegClientProtocolFactory())

    def buildProtocol(self, addr):
        logging.debug("build protocol for %s" % addr)
        protocol = MelkwegLocalProxyProtocol(
                addr.host, addr.port, MelkwegClientProtocolFactory.outgoing)
        return protocol

if __name__ == '__main__':
    reactor.listenTCP(config.CLIENT_PORT, MelkwegLocalProxyFactory())
    reactor.run()
