from cryptography.hazmat.primitives.ciphers.aead import AESCCM

key = AESCCM.generate_key(bit_length=256)
print(key)
with open('master_key.key', 'wb') as file:
    file.write(key)  # The key is type bytes still
    file.close()
