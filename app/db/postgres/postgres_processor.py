from __future__ import annotations

from app.config.logging_config import logger
from app.db.db_processor_base import DbProcessorBase
from app.db.postgres.pg_queries import fetch_token_by_user_id_and_client, update_token_by_user_id_and_client, \
    fetch_chunk, fetch_message_data
from app.db.postgres.pg_utils import fetch_all, execute
from app.decorators.try_catch_decorator import try_catch_wrapper
from app.dto.chat_message_db_record import ChatMessageDbRecord
from app.dto.chunk_db_record import ChunkDbRecord
from app.dto.token_metadata import TokenMetadata
from app.utils.application_constants import db_fetch_token_failed, db_token_update_failed, db_fetch_chunks_failed, \
    db_fetch_chat_failed


class PostgresProcessor(DbProcessorBase):

    @try_catch_wrapper(logger_fn= lambda e: logger.error(db_fetch_token_failed, exc_info=e))
    async def fetch_tokens(self, user_uuid: str, external_client: str) -> list[TokenMetadata] | None:
        rows = await fetch_all(fetch_token_by_user_id_and_client, user_uuid, external_client)
        if not rows: return None
        final_result = [TokenMetadata(**dict(row)) for row in rows]
        return final_result

    @try_catch_wrapper(logger_fn= lambda e: logger.error(db_token_update_failed, exc_info=e))
    async def update_token_by_user_id_and_external_client(self, user_uuid: str, token_data: TokenMetadata, external_client: str):
        await execute(update_token_by_user_id_and_client,
                      token_data.access_token, token_data.refresh_token, token_data.expires_at, user_uuid, external_client)

    @try_catch_wrapper(logger_fn= lambda e: logger.error(db_fetch_chunks_failed, exc_info=e))
    async def fetch_chunks(self, chunk_ids: list[str]) -> list[ChunkDbRecord]:
        rows = await fetch_all(fetch_chunk, chunk_ids)
        return [ChunkDbRecord(chunk_content=row['chunk_content'], chunk_id=str(row['uuid'])) for row in rows]

    @try_catch_wrapper(logger_fn= lambda e: logger.error(db_fetch_chat_failed, exc_info=e))
    async def fetch_message_data(self, message_ids: list[str]) -> list[ChatMessageDbRecord]:
        rows = await fetch_all(fetch_message_data, message_ids)
        return [ChatMessageDbRecord(**dict(row)) for row in rows]