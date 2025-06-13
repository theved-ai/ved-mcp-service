from typing import List

from qdrant_client.async_qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from app.dto.vector_client_request import VectorClientRequest
from app.dto.vector_client_response import VectorClientResponse
from app.utils.constants import QDRANT_GRPC_URL, THRESHOLD_VECTOR_MATCHING_SCORE
from app.webclients.pensieve.vector_client_base import VectorClientBase


def _generate_qdrant_query(query_metadata: dict) -> Filter | None:
    if not query_metadata:
        return None

    conditions = [
        FieldCondition(
            key=key,
            match=MatchValue(value=value)
        )
        for key, value in query_metadata.items()
        if value is not None
    ]

    return Filter(must=conditions)


class QdrantVectorClient(VectorClientBase):

    def __init__(self):
        self.async_qdrant_client = AsyncQdrantClient(url=QDRANT_GRPC_URL)

    async def fetch_matching_vectors(self, vector_req: VectorClientRequest) -> List[VectorClientResponse]:
        qdrant_query = _generate_qdrant_query(vector_req.query_metadata)

        matching_vectors = await self.async_qdrant_client.query_points(
            collection_name=vector_req.collection_name,
            query=vector_req.query_vector,
            query_filter=qdrant_query,
            limit=vector_req.max_matching_records,
            score_threshold=THRESHOLD_VECTOR_MATCHING_SCORE
        )

        return [VectorClientResponse(
            chunk_id=vector_record.payload['chunk_id'],
            chunk_data_source=vector_record.payload['data_input_source'],
            chunk_ingested_at=vector_record.payload['ingestion_timestamp'],
            content_timestamp=vector_record.payload['content_timestamp'],
            metadata=vector_record.payload['metadata'],
        ) for vector_record in matching_vectors.points]
