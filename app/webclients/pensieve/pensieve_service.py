from typing import List

from app.dto.pensieve_request import PensieveRequest
from app.dto.pensieve_response import PensieveResponse
from app.dto.search_chat_req import SearchChatRequest
from app.dto.vector_client_request import from_pensieve_req
from app.enums.input_data_source import InputDataSource
from app.utils.application_constants import EMBEDDING_MODEL_NAME
from app.webclients.pensieve.embedder import Embedder
from app.webclients.pensieve.qdrant_vector_client import QdrantVectorClient
from app.webclients.pensieve.text_extraction.vector_text_extraction_factory import get_text_extraction_service


async def generate_response_from_vector_records(matching_vectors):
    text_generation_service = get_text_extraction_service(InputDataSource(matching_vectors[0].chunk_data_source))
    return await text_generation_service.extract_text_from_vector(matching_vectors)


class PensieveService:

    def __init__(self):
        self.vector_service = QdrantVectorClient()
        self.embedding_service = Embedder()

    async def fetch_matching_chunks(self, req: PensieveRequest) -> List[PensieveResponse]:
        vector_representation = self.embedding_service.generate_vector(req.user_prompt)
        matching_vectors = await self.vector_service.fetch_matching_vectors(from_pensieve_req(req, vector_representation))
        return await generate_response_from_vector_records(matching_vectors)

    async def search_chat(self, req: SearchChatRequest):
        collection_name = f"{req.user_id}__{EMBEDDING_MODEL_NAME.replace('/', '_')}"
        vector_records = await self.vector_service.fetch_latest_messages(
            collection=collection_name,
            conversation_id=req.conversation_id,
            limit=req.max_messages
        )
        return await generate_response_from_vector_records(vector_records)