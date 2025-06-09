import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import hashlib

SECRET_KEY = hashlib.sha256(b"theved.ai").digest()

def decrypt_token(db_token: str) -> str:
    combined = bytes.fromhex(db_token)
    nonce = combined[:12]
    encrypted = combined[12:]
    aesgcm = AESGCM(SECRET_KEY)
    decrypted = aesgcm.decrypt(nonce, encrypted, None)
    return decrypted.decode("utf-8")

def encrypt_token(token: str) -> str:
    aesgcm = AESGCM(SECRET_KEY)
    nonce = os.urandom(12)
    encrypted = aesgcm.encrypt(nonce, token.encode(), None)
    return (nonce + encrypted).hex()

# if __name__ == '__main__':
#     token = encrypt_token('1//0g6meJl6A6_lSCgYIARAAGBASNwF-L9Ir-otZOyMwWhJiHX7AyqFqH5gJhunDIG6n9RlN-D3ur3SCdkv7-3qvH9hn3iBmNdNiBj4')
#     print(token)