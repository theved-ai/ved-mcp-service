from app.db.db_reader import fetch_tokens
from app.utils.token_decryption import decrypt_token
from mcp.server.fastmcp import Context

async def fetch_user_token_records(user_uuid: str, external_client: str):
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
        }
        decrypted_tokens_data.append(decrypted)

    return decrypted_tokens_data


async def fetch_user_token(user_uuid: str, external_client: str):
    records = await fetch_user_token_records(user_uuid, external_client)
    tokens = [row["access_token"] for row in records]
    return tokens

async def fetch_user_uuid(ctx: Context):
    header_dict = {k.decode().lower(): v.decode() for k, v in ctx.request_context.request.headers.raw}
    return header_dict.get("user_uuid")
