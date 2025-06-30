import json
from typing import List

from app.config.logging_config import logger
from app.db.db_processor import fetch_message_data
from app.dto.pensieve_response import PensieveResponse
from app.dto.vector_client_response import VectorClientResponse
from app.enums.input_data_source import InputDataSource
from app.webclients.pensieve.text_extraction.text_extraction_base import TextExtractionBase


class ChatDataSourceService(TextExtractionBase):

    def supported_data_input_source(self) -> InputDataSource:
        return InputDataSource.CHAT

    async def extract_text_from_vector(self, vector_records: List[VectorClientResponse]):
        message_ids = [vector_record.metadata.get('message_id') for vector_record in vector_records]
        message_records = await fetch_message_data(message_ids)
        message_dict = {str(record.message_id): record.content for record in message_records}

        responses = []
        for matching_vector in vector_records:
            message_id = matching_vector.metadata.get('message_id')
            if message_id not in message_dict:
                logger.warning(f"Message ID {message_id} found in vector DB but missing in message store. Skipping.")
                continue

            responses.append(PensieveResponse(
                chunk_content=message_dict[message_id],
                chunk_data_source=matching_vector.chunk_data_source,
                user_ingested_chunk_at=matching_vector.chunk_ingested_at,
                chunk_creation_timestamp=matching_vector.content_timestamp,
                chunk_metadata=matching_vector.metadata
            ))

        return responses