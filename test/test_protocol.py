#coding=utf-8

import os
import sys
import pytest
import logging

from twisted.trial import unittest
from twisted.test import proto_helpers
from twisted.internet import defer
from twisted.python import log

from protocol import MelkwegClientProtocol, MelkwegServerProtocol, ProtocolStatus
from packet_factory import PacketFactory

class FakeTransport(object):
    def __init__(self):
        self.buffer = []

    def write(self, data):
        self.buffer.append(data)

class TestProtocol(unittest.TestCase):
    def test_ping_pong(self):
        server = MelkwegServerProtocol()
        client = MelkwegClientProtocol()

        server_fake_transport = FakeTransport()
        client_fake_transport = FakeTransport()

        server.transport = server_fake_transport
        client.transport = client_fake_transport

        client.connectionMade()
        self.assertEqual(len(client_fake_transport.buffer), 1)

        server.stringReceived(client_fake_transport.buffer[-1])
        self.assertEqual(server.status, ProtocolStatus.RUNNING)

        client.stringReceived(server_fake_transport.buffer[-1])
        self.assertEqual(client.status, ProtocolStatus.RUNNING)

        packet1 = PacketFactory.create_data_packet(1234, "hello world")
        client.write(packet1)


