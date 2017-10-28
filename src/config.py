#coding=utf-8

import logging
from twisted.python import log

observer = log.PythonLoggingObserver()
observer.start()

fmt = "%(levelname)-8s %(asctime)-15s [%(filename)s:%(lineno)d] %(message)s"
logging.basicConfig(format=fmt, level=logging.INFO)

SERVER = "127.0.0.1"
SERVER_PORT = 23456
CLIENT_PORT = 23457
KEY = "if you stand, if you are true"

SERVER_SOCKS5_ADDR = "127.0.0.1"
SERVER_SOCKS5_PORT = 23458
