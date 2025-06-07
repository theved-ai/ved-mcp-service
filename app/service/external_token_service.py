from app.db.db_processor import fetch_tokens, update_token_by_user_id_and_external_client
from app.utils.token_security_util import decrypt_token, encrypt_token


async def fetch_external_token_records(user_uuid: str, external_client: str):
    encrypted_token_records = await fetch_tokens(user_uuid, external_client)
    if not encrypted_token_records:
        return None

    decrypted_tokens_data = []
    for token_data in encrypted_token_records:
        decrypted = {
            **token_data,
            "access_token": decrypt_token(token_data["access_token"]) if token_data["access_token"] else None,
            "refresh_token": decrypt_token(token_data["refresh_token"]) if token_data["refresh_token"] else None,
            "expires_at": token_data["expires_at"] if token_data["expires_at"] else None,
            "metadata": token_data["metadata"] if token_data["metadata"] else None
        }
        decrypted_tokens_data.append(decrypted)

    return decrypted_tokens_data

async def update_external_token(token_data, external_client, user_uuid):
    token_data_encrypted = {
        "access_token": encrypt_token(token_data["access_token"]) if token_data["access_token"] else None,
        "refresh_token": encrypt_token(token_data["refresh_token"]) if token_data["refresh_token"] else None,
        "expires_at": token_data["expires_at"]
    }
    await update_token_by_user_id_and_external_client(user_uuid, token_data_encrypted, external_client)


async def fetch_user_access_token(user_uuid: str, external_client: str):
    records = await fetch_external_token_records(user_uuid, external_client)
    tokens = [row["access_token"] for row in records]
    return tokens
