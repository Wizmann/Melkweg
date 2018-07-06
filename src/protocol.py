#coding=utf-8 
from enum import Enum
import time
import logging

from twisted.internet import defer, protocol, reactor, error
from twisted.protocols.basic import Int32StringReceiver
from twisted.protocols.policies import TimeoutMixin

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

def to_millisec(sec):
    return sec / 1000.

def timestamp():
    return int(time.time() * 1000)

class MelkwegProtocolBase(Int32StringReceiver, TimeoutMixin):
    def __init__(self):
        self.key = config.KEY
        self.iv = nonce(16)
        self.aes = AES_CTR(self.key, self.iv)
        self.state = ProtocolState.READY
        self.d = {} 
        self.setTimeout(config.TIMEOUT)
        logging.info("[%d] self iv: %s" % (id(self), hexlify(self.iv)))

    def heartbeat(self):
        assert self.is_client()
        try:
            packet = PacketFactory.create_liv_packet()
            packet.client_time = timestamp()

            self.write(packet)
            reactor.callLater(config.HEARTBEAT, self.heartbeat)
        except Exception, e:
            logging.error("error on heartbeat: %s" % e)
            reactor.callLater(config.HEARTBEAT, self.heartbeat)

    def is_server(self):
        return 'SERVER' in self.__class__.__dict__

    def is_client(self):
        return 'CLIENT' in self.__class__.__dict__

    def write(self, packet):
        data = packet.SerializeToString()
        logging.debug("[%d] write data [packet:%d|state:%s]" % (id(self), len(data), self.state))
        if self.state == ProtocolState.READY:
            self.sendString(data)
        else:
            self.sendString(self.aes.encrypt(data))

    def stringReceived(self, string):
        logging.debug("[%d] string received: %d, state: %s" % (id(self), len(string), self.state))

        mpacket = self.parse(string)

        if mpacket == None:
            self.handle_error()

        if self.state == ProtocolState.READY:
            if mpacket.iv != None:
                self.peer_aes = AES_CTR(self.key, mpacket.iv)
                logging.info("[%d] get iv: %s from %s" % (id(self), hexlify(mpacket.iv), self.transport.getPeer()))

                if self.is_server():
                    self.write(PacketFactory.create_syn_packet(self.iv))

                self.state = ProtocolState.RUNNING

                if self.is_client():
                    self.heartbeat()
            else:
                self.handle_error()

        elif self.state == ProtocolState.RUNNING:
            if mpacket.flags == PacketFlag.DATA:
                self.handleDataPacket(mpacket)
            elif mpacket.flags in [PacketFlag.RST, PacketFlag.FIN]:
                logging.debug("connection on port %d will be terminated" % mpacket.port)
                if self.is_server() and mpacket.port in self.d:
                    if self.d[mpacket.port].transport:
                        self.d[mpacket.port].transport.loseConnection()
                if mpacket.port in self.d:
                    del self.d[mpacket.port]
            elif mpacket.flags == PacketFlag.LIV:
                if self.is_server():
                    packet = PacketFactory.create_liv_packet()
                    packet.client_time = mpacket.client_time
                    packet.server_time = timestamp()
                    self.write(packet)

                if self.is_client():
                    client_time = mpacket.client_time
                    logging.warn("[%d][HEARTBEAT] ping = %d ms" % (id(self), timestamp() - client_time))

                self.resetTimeout()
            else:
                self.handle_error()
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
            logging.error('[%d]: %s' %(id(self), e))
            self.handle_error()

class MelkwegServerOutgoingProtocol(protocol.Protocol):
    def __init__(self, peersock, port):
        self.peersock = peersock
        self.port = port
        self.peersock.d[self.port] = self

    def dataReceived(self, data):
        self.peersock.write(PacketFactory.create_data_packet(self.port, data))

    def connectionLost(self, reason):
        logging.debug("outgoing protocol on port %d is lost: %s" % (self.port, reason))
        if reason.check(error.ConnectionDone):
            self.peersock.write(PacketFactory.create_fin_packet(self.port))
        else:
            self.peersock.write(PacketFactory.create_rst_packet(self.port))

class MelkwegServerProtocol(MelkwegProtocolBase):
    SERVER = True
    def connectionMade(self):
        logging.debug("[%d] connection is made" % id(self))

    def connectionLost(self, reason):
        logging.error("connection to client %s is lost, %s" % (self.transport.getPeer(), reason))

    def handleDataPacket(self, mpacket):
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

    def handleDataPacket(self, mpacket):
        port = mpacket.port
        if port in self.d:
            self.d[port].transport.write(mpacket.data)
        else:
            self.write(PacketFactory.create_rst_packet(port))
