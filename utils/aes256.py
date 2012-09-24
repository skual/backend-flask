# coding=utf-8

from Crypto import Random
from Crypto.Cipher import AES

import base64
import hashlib

from configs import project

# @see http://stackoverflow.com/questions/12524994/encrypt-decrypt-using-pycrypto-aes-256/12525165#12525165

BLOCK_SIZE=32

pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s : s[0:-ord(s[-1])]

def encrypt(message, passphrase):
    # Make a 32bit key
    passphrase = hashlib.sha256(project['SECRET_KEY'] + passphrase).digest()
    iv = Random.new().read(AES.block_size)

    aes = AES.new(passphrase, AES.MODE_CBC, iv)
    encrypted = aes.encrypt(pad(message))
    return base64.b64encode(encrypted)

def decrypt(encrypted, passphrase):
    # Make a 32bit ke :
    passphrase = hashlib.sha256(project['SECRET_KEY'] + passphrase).digest()
    decoded = base64.b64decode(encrypted)

    iv = decoded[:16]

    aes = AES.new(passphrase, AES.MODE_CBC, iv)
    return unpad(aes.decrypt(decoded))