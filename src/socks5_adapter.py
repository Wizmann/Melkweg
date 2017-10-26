#coding=utf-8

from packet_pb2 import MPacket
from packet_factory import PacketFactory

class MelkwegProtocolTransportAdapter(object):
    def __init__(self, protocol, port):
        self.protocol = protocol
        self.port = port

    def write(self, data):
        packet = PacketFactory.create_data_packet(self.port, data)
        self.protocol.write(packet)

    def loseConnection(self):
        self.protocol.handle_lose_connection(self.port)

    def startReading(self):
        self.protocol.transport.startReading()

    def stopReading(self):
        self.protocol.transport.stopReading()
