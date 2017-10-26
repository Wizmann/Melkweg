#coding=utf-8

import logging
from twisted.internet import protocol, reactor, defer
from twisted.python import log

import config
from protocol import MelkwegServerProtocol

observer = log.PythonLoggingObserver()
observer.start()

fmt = "%(levelname)-8s %(asctime)-15s [%(filename)s:%(lineno)d] %(message)s"
logging.basicConfig(format=fmt, level=logging.NOTSET)

class MelkwegServerFactory(protocol.Factory):
    protocol = MelkwegServerProtocol

    def buildProtocol(self, addr):
        logging.debug("build protocol for %s" % addr)
        return self.protocol()

if __name__ == '__main__':
    reactor.listenTCP(config.SERVER_PORT, MelkwegServerFactory())
    reactor.run()

