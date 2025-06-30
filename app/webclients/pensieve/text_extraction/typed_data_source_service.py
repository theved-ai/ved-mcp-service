from typing import List

from app.db.postgres.postgres_processor import PostgresProcessor
from app.dto.pensieve_response import PensieveResponse
from app.dto.vector_client_response import VectorClientResponse
from app.enums.input_data_source import InputDataSource
from app.webclients.pensieve.text_extraction.text_extraction_base import TextExtractionBase
from app.config.logging_config import logger


class TypedDataSourceService(TextExtractionBase):

    def __init__(self):
        self.storage_service = PostgresProcessor()

    def supported_data_input_source(self) -> InputDataSource:
        return InputDataSource.USER_TYPED

    async def extract_text_from_vector(self, vector_records: List[VectorClientResponse]):
        chunk_ids = [matching_vector.chunk_id for matching_vector in vector_records]
        chunk_db_records = await self.storage_service.fetch_chunks(chunk_ids)
        chunk_dict = {record.chunk_id: record.chunk_content for record in chunk_db_records}

        responses = []
        for matching_vector in vector_records:
            chunk_id = matching_vector.chunk_id
            if chunk_id not in chunk_dict:
                logger.warning(f"Chunk ID {chunk_id} found in vector DB but missing in chunk store. Skipping.")
                continue

            responses.append(PensieveResponse(
                chunk_content=chunk_dict[chunk_id],
                chunk_data_source=matching_vector.chunk_data_source,
                user_ingested_chunk_at=matching_vector.chunk_ingested_at,
                chunk_creation_timestamp=matching_vector.content_timestamp,
                chunk_metadata=matching_vector.metadata
            ))

        return responses