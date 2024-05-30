from typing import Any
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

import base64
import os

class Signer:

    def __init__(self, identifier):

        self.identifier = ''.join(c for c in identifier if c not in '?!/;').replace("http:","").replace(":",".")

        # If the pubkey and privkeys exist, load them and store as pubkey and privkey
        if os.path.isfile('./pem/pubkey-'+self.identifier+'.pem') and os.path.isfile('./pem/privkey-'+self.identifier+'.pem'): 

            with open('./pem/pubkey-'+self.identifier+'.pem', "rb") as key_file:
                self.public_key = serialization.load_pem_public_key(key_file.read())

            with open('./pem/privkey-'+self.identifier+'.pem', "rb") as key_file:
                self.private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=None,
                )
            
            return

        # Else create and store pubkey and privkey
        else: 
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )
            self.privkey_pem = self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            with open('./pem/privkey-'+self.identifier+'.pem', 'wb') as pem_out:
                pem_out.write(self.privkey_pem)
            
            self.public_key = self.private_key.public_key()
            self.pubkey_pem = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            with open('./pem/pubkey-'+self.identifier+'.pem', 'wb') as pem_out:
                pem_out.write(self.pubkey_pem)

    def sign_transaction(self, transaction):
        print(transaction.stringify())
    
    # Accepts a bytearray and generates a base64 encoded signature (bytes)
    def generate_signature(self, message_bytes):
        signature = self.private_key.sign(
            message_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ), 
            hashes.SHA256()
        )
        return base64.b64encode(signature)

    def get_pubkey(self):
        return self.pubkey_pem