#coding=utf-8

import logging
from twisted.python import log

observer = log.PythonLoggingObserver()
observer.start()

fmt = "%(levelname)-8s %(asctime)-15s [%(filename)s:%(lineno)d] %(message)s"
logging.basicConfig(format=fmt, level=logging.INFO)

TIMEOUT = 60
HEARTBEAT = 10
CLIENT_OUTGOING_CONN_NUM = 5
SOCKS5_OUTGOING_PROTOCOL_TIMEOUT = 30

CIPHER = "AES_CTR_HMAC"

SERVER = "127.0.0.1"
SERVER_PORT = 20000
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

USE_LOCAL_DNS = True
REMOTE_DNS_SERVICE_ADDRS = [('8.8.4.4', 53)]
LOCAL_DNS_SERVICE_UDP_PORT = 20053
LOCAL_DNS_SERVICE_TCP_PORT = 20053
