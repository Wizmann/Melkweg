#coding=utf-8

from __future__ import absolute_import

import abc
import binascii
import random
from Crypto.Cipher import AES
from Crypto.Util import Counter
import Crypto.Hash.SHA256
import config
from Crypto.Util.number import bytes_to_long

def digest(plain_text, length=16):
    h = Crypto.Hash.SHA256.new()
    h.update(plain_text)
    return h.digest()[:length]

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

def factory(cipher, *args):
    if cipher == "AES_CTR":
        return AES_CTR(*args)
    elif cipher == "AES_CTR_HMAC":
        return AES_CTR_HMAC(*args)
    else:
        raise Exception("No cipher: %s is found" % cipher)


class AES_CTR(ICipher):
    def __init__(self, key, iv):
        ctr = Counter.new(128, initial_value=bytes_to_long(iv))
        self.aes = AES.new(digest(key), AES.MODE_CTR, counter=ctr)

    def encrypt(self, plain_data):
        return self.aes.encrypt(plain_data)

    def decrypt(self, encrypted_data):
        return self.aes.decrypt(encrypted_data)

class AES_CTR_HMAC(ICipher):
    HMAC_LEN = 16
    def __init__(self, key, iv):
        self.hmac_key = config.HMAC_KEY
        ctr = Counter.new(128, initial_value=bytes_to_long(iv))
        self.aes = AES.new(digest(key), AES.MODE_CTR, counter=ctr)

    def encrypt(self, plain_data):
        encrypted = self.aes.encrypt(plain_data)
        tag = digest(self.hmac_key + plain_data + self.hmac_key, self.HMAC_LEN)
        return encrypted + tag

    def decrypt(self, encrypted_data):
        tag = encrypted_data[-self.HMAC_LEN:]
        encrypted = encrypted_data[:-self.HMAC_LEN]
        decrypted = self.aes.decrypt(encrypted)

        tag2 = digest(self.hmac_key + decrypted + self.hmac_key, self.HMAC_LEN)
        if tag != tag2:
            raise Exception("hmac check error")
        return decrypted
