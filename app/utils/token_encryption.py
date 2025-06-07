import hashlib
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

SECRET_KEY = hashlib.sha256(b"theved.ai").digest()

def encrypt_token(token: str) -> str:
    aesgcm = AESGCM(SECRET_KEY)
    nonce = os.urandom(12)
    encrypted = aesgcm.encrypt(nonce, token.encode(), None)
    return (nonce + encrypted).hex()  # Store this as a single field


if __name__ == '__main__':
    token = encrypt_token('1//0g5IXmQs3eveQCgYIARAAGBASNwF-L9IrgjHlvrLSArfXmN_gL697e7MQg_YtiYheJUi7FoC6DZtGE3nOsPpDS7fqUu02O7ZEzsc')
    print(token)
