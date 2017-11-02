#coding=utf-8

from packet_pb2 import MPacket
from cipher import nonce

class PacketFlag(object):
    DATA = 1
    LIV = 2
    RST = 3
    FIN = 4
    KILL = 5

class PacketFactory(object):
    @classmethod
    def create_syn_packet(self, iv):
        packet = MPacket()
        packet.iv = iv
        return packet

    @classmethod
    def create_rst_packet(self, port):
        packet = MPacket()
        packet.port = port
        packet.flags = PacketFlag.RST
        return packet

    @classmethod
    def create_kill_packet(self):
        packet = MPacket()
        packet.flags = PacketFlag.KILL
        return packet

    @classmethod
    def create_data_packet(self, port, data):
        packet = MPacket()
        packet.flags = PacketFlag.DATA
        packet.port = port
        packet.data = data
        return packet

    @classmethod
    def create_fin_packet(self, port):
        packet = MPacket()
        packet.flags = PacketFlag.FIN
        packet.port = port
        return packet
