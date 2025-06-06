from app.db.db_reader import fetch_tokens
from app.utils.token_decryption import decrypt_token
from mcp.server.fastmcp.server import Context

async def fetch_user_token(ctx: Context, external_client: str):
    header_dict = {k.decode().lower(): v.decode() for k, v in ctx.request_context.request.headers.raw}
    user_uuid = header_dict.get("user_uuid")
    encrypted_token_records = await fetch_tokens(user_uuid, external_client)
    if not encrypted_token_records:
        return None
    tokens = [decrypt_token(row["access_token"]) for row in encrypted_token_records]
    return tokens
