#coding=utf-8

from __future__ import absolute_import

import abc
import binascii
import random
from Crypto.Cipher import AES
from Crypto.Util import Counter
import Crypto.Hash.MD5
from Crypto.Util.number import bytes_to_long

def digest(plain_text):
    h = Crypto.Hash.MD5.new()
    h.update(plain_text)
    return h.digest()

def nonce(length):
    return ''.join([chr(random.randint(0, 255)) for i in xrange(length)])

def hexlify(binary):
    return binascii.hexlify(binary)

class ICipher(object):
    __metaclass__ = abc.ABCMeta

    def encrypt(self, plain_data):
        pass

    def decrypt(self, encrypted_data):
        pass

class AES_CTR(ICipher):
    def __init__(self, key, iv):
        ctr = Counter.new(128, initial_value=bytes_to_long(iv))
        self.aes = AES.new(digest(key), AES.MODE_CTR, counter=ctr)

    def encrypt(self, plain_data):
        return self.aes.encrypt(plain_data)

    def decrypt(self, encrypted_data):
        return self.aes.decrypt(encrypted_data)
