#coding=utf-8

import logging
from twisted.internet import protocol, reactor, defer

import config
from protocol import MelkwegServerProtocol
from socks5 import SOCKSv5

class MelkwegServerFactory(protocol.Factory):
    protocol = MelkwegServerProtocol

    def buildProtocol(self, addr):
        logging.debug("build protocol for %s" % addr)
        return self.protocol()

class MelkwegSocks5ProtocolFactory(protocol.Factory):
    protocol = SOCKSv5

if __name__ == '__main__':
    if config.USE_KCP:
        from kcp_server import ServerProtocolFactory as KcpServerProtocolFactory

        reactor.listenTCP(config.SERVER_PORT, MelkwegServerFactory())
        reactor.listenTCP(config.SERVER_SOCKS5_PORT, MelkwegSocks5ProtocolFactory())
        reactor.listenUDP(config.SERVER_KCP_PORT, KcpServerProtocolFactory())
    else:
        reactor.listenTCP(config.SERVER_PORT, MelkwegServerFactory())
        reactor.listenTCP(config.SERVER_SOCKS5_PORT, MelkwegSocks5ProtocolFactory())

    reactor.run()
