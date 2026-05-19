#!/usr/bin/env python3
"""
Client-side encryption manager
"""

import os
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class CryptoManager:
    @staticmethod
    def encrypt_rsa(data: bytes, pub_key_pem: bytes) -> bytes:
        public_key = serialization.load_pem_public_key(pub_key_pem, backend=default_backend())
        return public_key.encrypt(
            data,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    
    @staticmethod
    def encrypt_aes(data: bytes, key: bytes) -> bytes:
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        pad_len = 16 - (len(data) % 16)
        padded = data + bytes([pad_len]) * pad_len
        
        encrypted = encryptor.update(padded) + encryptor.finalize()
        return base64.b64encode(iv + encrypted)
    
    @staticmethod
    def decrypt_aes(encrypted_data: bytes, key: bytes) -> bytes:
        data = base64.b64decode(encrypted_data)
        iv = data[:16]
        ciphertext = data[16:]
        
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded = decryptor.update(ciphertext) + decryptor.finalize()
        
        pad_len = padded[-1]
        return padded[:-pad_len]