from __future__ import annotations

from app.config.logging_config import logger
from app.db.postgres.postgres_processor import PostgresProcessor
from app.decorators.try_catch_decorator import try_catch_wrapper
from app.dto.token_metadata import TokenMetadata
from app.utils.application_constants import fetch_token_failed, token_update_failed, fetch_access_token_failed
from app.utils.token_security_util import decrypt_token, encrypt_token

class ExternalTokenService:

    def __init__(self):
        self.storage_service = PostgresProcessor()

    @try_catch_wrapper(logger_fn= lambda e: logger.error(fetch_token_failed, exc_info=e))
    async def fetch_external_token_records(self, user_uuid: str, external_client: str) -> list[TokenMetadata] | None:
        encrypted_token_records = await self.storage_service.fetch_tokens(user_uuid, external_client)
        if not encrypted_token_records: return None
        return [
            TokenMetadata(
                access_token=decrypt_token(token_data.access_token) if token_data.access_token else None,
                refresh_token=decrypt_token(token_data.refresh_token) if token_data.refresh_token else None,
                expires_at=token_data.expires_at if token_data.expires_at else None,
                metadata=token_data.metadata if token_data.metadata else None
            ) for token_data in encrypted_token_records
        ]

    @try_catch_wrapper(logger_fn= lambda e: logger.error(token_update_failed, exc_info=e))
    async def update_external_token(self, token_data: TokenMetadata, external_client, user_uuid):
        token_data_encrypted= TokenMetadata(
            access_token=encrypt_token(token_data.access_token) if token_data.access_token else None,
            refresh_token=encrypt_token(token_data.refresh_token) if token_data.refresh_token else None,
            expires_at=token_data.expires_at
        )
        await self.storage_service.update_token_by_user_id_and_external_client(user_uuid, token_data_encrypted, external_client)

    @try_catch_wrapper(logger_fn= lambda e: logger.error(fetch_access_token_failed, exc_info=e))
    async def fetch_user_access_token(self, user_uuid: str, external_client: str):
        tokens_metadata = await self.fetch_external_token_records(user_uuid, external_client)
        access_tokens = [token_metadata.access_token for token_metadata in tokens_metadata]
        return access_tokens
