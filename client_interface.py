from cryptography.hazmat.primitives.ciphers.aead import AESCCM
from cryptography.hazmat.backends import default_backend
import os
import shutil


chunk_size = 256
nonce = bytes("0123456789012345", 'utf-8')
with open('master_key.key', 'rb') as key_file:
    key = key_file.read()

print(key)
aes = AESCCM(key=key)

uploaded_file = 'ejemplo.txt'
with open(uploaded_file, "rb") as source, open('encrypted.txt', 'wb+') as sink:
    byte = source.read(chunk_size)
    while byte:
        sink.write(aes.update(byte))
        byte = source.read(chunk_size)

    source.close()
    sink.close()

decryptor = cipher.decryptor()
#GET: Encrypt a file into secure folder
file_to_get = "encrypted.txt"
with open(file_to_get, "rb") as source, open('decrypted.txt', "wb+") as sink:
    byte = source.read(chunk_size)
    while byte:
        sink.write(decryptor.update(byte))
        # Do stuff with byte.
        byte = source.read(chunk_size)
    source.close()
    sink.close()
