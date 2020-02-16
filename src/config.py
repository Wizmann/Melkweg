#coding=utf-8

import logging
from twisted.python import log

observer = log.PythonLoggingObserver()
observer.start()

fmt = "%(levelname)-8s %(asctime)-15s [%(filename)s:%(lineno)d] %(message)s"
logging.basicConfig(format=fmt, level=logging.INFO)

TIMEOUT = 60
HEARTBEAT = 10
CLIENT_OUTGOING_CONN_NUM = 10
SOCKS5_OUTGOING_PROTOCOL_TIMEOUT = 30

CIPHER = "AES_CTR_HMAC"

SERVER = '127.0.0.1'
SERVER_PORT = 20010
CLIENT_PORT = 20001
KEY = "if you stand, if you are true"

SERVER_SOCKS5_ADDR = "127.0.0.1"
SERVER_SOCKS5_PORT = 20002

USE_KCP = False
KCP_WINDOW_SIZE = 1024

CLIENT_KCP_ADDR = "127.0.0.1"
CLIENT_KCP_PORT = 20010

SERVER_KCP_ADDR = "127.0.0.1"
SERVER_KCP_PORT = 20011
