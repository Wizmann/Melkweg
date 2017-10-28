#coding=utf-8 
from enum import Enum
import logging

from twisted.python import log
from twisted.internet import defer, protocol, reactor
from twisted.protocols.basic import Int32StringReceiver

from packet_pb2 import MPacket

import config
from cipher import AES_CTR, nonce, hexlify
from socks5 import SOCKSv5
from socks5_adapter import MelkwegProtocolTransportAdapter
from packet_factory import PacketFactory, PacketFlag

class ProtocolState(Enum):
    READY = 1
    RUNNING = 2
    DONE = 3
    ERROR = 4

class MelkwegServerProtocolBase(Int32StringReceiver):
    def __init__(self):
        self.key = config.KEY
        self.iv = nonce(16)
        self.aes = AES_CTR(self.key, self.iv)
        self.state = ProtocolState.READY
        self.d = {} 
        logging.info("self iv: %s" % hexlify(self.iv))

    def write(self, packet, raw=False):
        data = packet.SerializeToString()
        logging.debug("write data [packet:%d|raw:%s]" % (len(data), raw))
        if raw:
            self.sendString(data)
        else:
            self.sendString(self.aes.encrypt(data))

    def read(self, data):
        return self.peer_aes.decrypt(data)

    def is_server(self):
        return 'SERVER' in self.__class__.__dict__

    def is_client(self):
        return 'CLIENT' in self.__class__.__dict__

    def connectionMade(self):
        logging.debug("connection is made")
        if self.is_client():
            self.write(PacketFactory.create_syn_packet(self.iv), raw=True)

    def stringReceived(self, string):
        logging.debug("string received: %d, state: %s" % (len(string), self.state))

        if self.state == ProtocolState.READY:
            mpacket = self.parse(string, raw=True)
            if mpacket == None:
                self.handle_error()
                logging.error("error on READY state")
            elif mpacket.iv != None:
                self.peer_aes = AES_CTR(self.key, mpacket.iv)
                self.state = ProtocolState.RUNNING

                logging.info("get iv: %s" % hexlify(mpacket.iv))

                if self.is_server():
                    self.write(PacketFactory.create_syn_packet(self.iv), raw=True)
            else:
                self.write(PacketFactory.create_rst_packet())
                self.state = ProtocolState.ERROR
                self.transport.loseConnection()
        elif self.state == ProtocolState.RUNNING:
            mpacket = self.parse(string)
            if mpacket == None:
                logging.error("error on RUNNING state")
                self.handle_error()
            elif mpacket.iv:
                logging.error("iv on RUNNING state, %s" % hexlify(mpacket.iv))
                self.handle_error()
            elif mpacket.flags == PacketFlag.DATA:
                self.handle_data_packet(mpacket)
            elif mpacket.flags == PacketFlag.RST:
                port = mpacket.port
                if port in self.d:
                    del self.d[port]
            elif mpacket.flags == PacketFlag.FIN:
                if self.is_server():
                    port = mpacket.port
                    if port in self.d:
                        del self.d[port]
        else:
            self.handle_error()

    def handle_error(self):
        logging.error("handle error")
        self.state = ProtocolState.ERROR
        self.transport.loseConnection()

    def handle_lose_connection(self, port):
        self.write(PacketFactory.create_fin_packet(port))
        logging.debug("shutdown port %d" % port)
        if port in self.d:
            del self.d[port]
        else:
            logging.error("port %d not in dict" % port)

    def handle_data_packet(self, mpacket):
        port = mpacket.port
        if self.is_server():
            if port not in self.d:
                socks = SOCKSv5()
                socks.transport = MelkwegProtocolTransportAdapter(self, port)
                self.d[port] = socks
            self.d[port].dataReceived(mpacket.data)
        elif self.is_client():
            if port in self.d:
                self.d[port].transport.write(mpacket.data)

    def connectionLost(self, reason):
        if self.is_client():
            logging.error("server connection is lost")
            for (port, proxy) in self.d.items():
                proxy.transport.loseConnection()

    def parse(self, string, raw=False):
        mpacket = MPacket()
        try:
            if raw:
                mpacket.ParseFromString(string)
            else:
                mpacket.ParseFromString(self.read(string))
            return mpacket
        except Exception, e:
            logging.error(e)
            return None



class MelkwegServerProtocol(MelkwegServerProtocolBase):
    SERVER = True

class MelkwegClientProtocol(MelkwegServerProtocolBase):
    CLIENT = True
