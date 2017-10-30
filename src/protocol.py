#coding=utf-8 
from enum import Enum
import logging

from twisted.internet import defer, protocol, reactor, error
from twisted.protocols.basic import Int32StringReceiver

from packet_pb2 import MPacket

import config
from cipher import AES_CTR, nonce, hexlify
from socks5 import SOCKSv5
from packet_factory import PacketFactory, PacketFlag

class ProtocolState(Enum):
    READY = 1
    RUNNING = 2
    DONE = 3
    ERROR = 4

class MelkwegProtocolBase(Int32StringReceiver):
    def __init__(self):
        self.key = config.KEY
        self.iv = nonce(16)
        self.aes = AES_CTR(self.key, self.iv)
        self.state = ProtocolState.READY
        self.d = {} 
        logging.info("self iv: %s" % hexlify(self.iv))

    def is_server(self):
        return 'SERVER' in self.__class__.__dict__

    def is_client(self):
        return 'CLIENT' in self.__class__.__dict__

    def write(self, packet):
        data = packet.SerializeToString()
        logging.debug("write data [packet:%d|state:%s]" % (len(data), self.state))
        if self.state == ProtocolState.READY:
            self.sendString(data)
        else:
            self.sendString(self.aes.encrypt(data))

    def stringReceived(self, string):
        logging.debug("string received: %d, state: %s" % (len(string), self.state))

        mpacket = self.parse(string)

        if mpacket == None:
            self.handle_error()
            return

        if self.state == ProtocolState.READY:
            if mpacket.iv != None:
                self.peer_aes = AES_CTR(self.key, mpacket.iv)
                logging.info("get iv: %s" % hexlify(mpacket.iv))

                if self.is_server():
                    self.write(PacketFactory.create_syn_packet(self.iv))

                self.state = ProtocolState.RUNNING
            else:
                self.handle_error()
        elif self.state == ProtocolState.RUNNING:
            if mpacket.flags == PacketFlag.DATA:
                self.handle_data_packet(mpacket)
            elif mpacket.flags in [PacketFlag.RST, PacketFlag.FIN]:
                if self.is_server:
                    self.d[mpacket.port].transport.loseConnection()
                if mpacket.port in self.d:
                    del self.d[mpacket.port]
        else:
            self.handle_error()

    def handle_error(self):
        logging.error("handle error")
        self.state = ProtocolState.ERROR
        self.transport.loseConnection()

    def parse(self, string):
        mpacket = MPacket()
        try:
            if self.state == ProtocolState.READY:
                mpacket.ParseFromString(string)
            else:
                plain_data = self.peer_aes.decrypt(string)
                mpacket.ParseFromString(plain_data)
            return mpacket
        except Exception, e:
            logging.error(e)
            return None

class MelkwegServerOutgoingProtocol(protocol.Protocol):
    def __init__(self, peersock, port):
        self.peersock = peersock
        self.port = port
        self.peersock.d[self.port] = self

    def dataReceived(self, data):
        self.peersock.write(PacketFactory.create_data_packet(self.port, data))

    def connectionLost(self, reason):
        if reason.check(error.ConnectionDone):
            self.peersock.write(PacketFactory.create_fin_packet(self.port))
        else:
            self.peersock.write(PacketFactory.create_rst_packet(self.port))

class MelkwegServerProtocol(MelkwegProtocolBase):
    SERVER = True
    def connectionMade(self):
        logging.debug("connection is made")

    def connectionLost(self, reason):
        logging.error("connection to client %s is lost" % self.transport.getPeer())

    def handle_data_packet(self, mpacket):
        port = mpacket.port

        if port not in self.d:
            protocol.ClientCreator(reactor, MelkwegServerOutgoingProtocol, self, port)\
                    .connectTCP(config.SERVER_SOCKS5_ADDR, config.SERVER_SOCKS5_PORT)\
                    .addCallback(lambda _: self.d[port].transport.write(mpacket.data))
        else:
            self.d[port].transport.write(mpacket.data)

class MelkwegClientProtocol(MelkwegProtocolBase):
    CLIENT = True
    def connectionMade(self):
        logging.debug("connection is made")
        self.write(PacketFactory.create_syn_packet(self.iv))

    def connectionLost(self, reason):
        logging.error("connection to server is lost")
        for (port, proxy) in self.d.items():
            proxy.transport.loseConnection()

    def handle_data_packet(self, mpacket):
        port = mpacket.port
        if port in self.d:
            self.d[port].transport.write(mpacket.data)
        else:
            self.write(PacketFactory.create_rst_packet(port))
