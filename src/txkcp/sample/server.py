#coding=utf-8

import os
import sys

sys.path.insert(0, os.path.abspath('src'))

import txkcp
import logging
from twisted.internet import protocol, reactor, defer

import config

class ServerProtocol(txkcp.Protocol):
    def __init__(self):
        self.addr = (config.CLIENT_ADDR, config.CLIENT_OUTGOING_PORT)
        txkcp.Protocol.__init__(self, self.addr, config.CONV_ID)

    def dataReceived(self, data):
        logging.info("data received: %s" % data)
        self.send("ack: %s" % data)

if __name__ == '__main__':
    reactor.listenUDP(config.SERVER_PORT, ServerProtocol())
    reactor.run()

