#coding=utf-8

import random
import logging
from twisted.internet import defer, protocol, reactor, error

import config
from protocol import MelkwegClientProtocol
from packet_factory import PacketFactory

if config.USE_KCP:
    from kcp_local import LocalProxyProtocolFactory as KcpLocalProxyProtocolFactory

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
    initialDelay = 3
    maxDelay = 10

    def buildProtocol(self, addr):
        self.outgoing = MelkwegClientProtocol()
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
    def __init__(self, host, port):
        self.outgoing = [
            MelkwegClientProtocolFactory()
            for i in xrange(config.CLIENT_OUTGOING_CONN_NUM)
        ]

        for outgoing in self.outgoing:
            reactor.connectTCP(host, port, outgoing)

    def buildProtocol(self, addr):
        logging.debug("build protocol for %s" % addr)
        outgoingProtocol = random.choice(self.outgoing)
        protocol = MelkwegLocalProxyProtocol(
                addr.host, addr.port, outgoingProtocol.outgoing)
        return protocol

if __name__ == '__main__':
    if config.USE_KCP:
        reactor.listenTCP(config.CLIENT_KCP_PORT, KcpLocalProxyProtocolFactory())
        reactor.listenTCP(
                config.CLIENT_PORT, 
                MelkwegLocalProxyFactory(config.CLIENT_KCP_ADDR, config.CLIENT_KCP_PORT))
    else:
        reactor.listenTCP(
                config.CLIENT_PORT, 
                MelkwegLocalProxyFactory(config.SERVER, config.SERVER_PORT))

    if config.USE_LOCAL_DNS:
        import localdns
        localdns.build_dns()

    reactor.run()
