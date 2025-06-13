from typing import List

from app.db.db_processor import fetch_chunks
from app.dto.pensieve_request import PensieveRequest
from app.dto.pensieve_response import PensieveResponse
from app.dto.vector_client_request import from_pensieve_req
from app.webclients.pensieve.embedder import Embedder
from app.webclients.pensieve.qdrant_vector_client import QdrantVectorClient


class PensieveService:

    def __init__(self):
        self.vector_service = QdrantVectorClient()
        self.embedding_service = Embedder()

    async def fetch_matching_chunks(self, req: PensieveRequest) -> List[PensieveResponse]:
        vector_representation = self.embedding_service.generate_vector(req.user_prompt)
        matching_vectors = await self.vector_service.fetch_matching_vectors(from_pensieve_req(req, vector_representation))
        chunk_ids = [matching_vector.chunk_id for matching_vector in matching_vectors]
        chunk_db_records = await fetch_chunks(chunk_ids)
        chunk_dict = {record['uuid']: record['chunk_content'] for record in chunk_db_records}

        return [PensieveResponse(
            chunk_content=chunk_dict.get(matching_vector.chunk_id),
            chunk_data_source=matching_vector.chunk_data_source,
            user_ingested_chunk_at=matching_vector.chunk_ingested_at,
            chunk_creation_timestamp=matching_vector.content_timestamp,
            chunk_metadata=matching_vector.metadata
        ) for matching_vector in matching_vectors]