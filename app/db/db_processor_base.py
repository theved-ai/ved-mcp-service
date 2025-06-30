from __future__ import annotations

from abc import ABC, abstractmethod

from app.dto.chat_message_db_record import ChatMessageDbRecord
from app.dto.chunk_db_record import ChunkDbRecord
from app.dto.token_metadata import TokenMetadata


class DbProcessorBase(ABC):

    @abstractmethod
    async def fetch_tokens(self, user_uuid: str, external_client: str) -> list[TokenMetadata] | None:
        pass

    @abstractmethod
    async def update_token_by_user_id_and_external_client(self, user_uuid: str, token_data: TokenMetadata, external_client: str) -> None:
        pass

    @abstractmethod
    async def fetch_chunks(self, chunk_ids: list[str]) -> list[ChunkDbRecord]:
        pass

    @abstractmethod
    async def fetch_message_data(self, message_ids: list[str]) -> list[ChatMessageDbRecord]:
        pass
