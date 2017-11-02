#coding=utf-8

import logging
from twisted.python import log

observer = log.PythonLoggingObserver()
observer.start()

fmt = "%(levelname)-8s %(asctime)-15s [%(filename)s:%(lineno)d] %(message)s"
logging.basicConfig(format=fmt, level=logging.NOTSET)


SERVER_ADDR = "127.0.0.1"
SERVER_PORT = 10003

CLIENT_ADDR = "127.0.0.1"
CLIENT_PORT = 10001
CLIENT_OUTGOING_PORT = 10002

CONV_ID = 12345
