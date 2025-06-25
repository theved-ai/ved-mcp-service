from datetime import datetime
from typing import Any
from typing import List

from qdrant_client.async_qdrant_client import AsyncQdrantClient
from qdrant_client.models import FieldCondition, Filter, Range

from app.dto.vector_client_request import VectorClientRequest
from app.dto.vector_client_response import VectorClientResponse
from app.utils.constants import QDRANT_GRPC_URL, THRESHOLD_VECTOR_MATCHING_SCORE
from app.webclients.pensieve.vector_client_base import VectorClientBase


def parse_iso8601_to_unix(value: str) -> float:
    return datetime.fromisoformat(value).timestamp()

def _generate_qdrant_query(query_metadata: dict[str, Any]) -> Filter | None:
    if not query_metadata:
        return None

    conditions = []
    for key, value in query_metadata.items():
        if isinstance(value, dict):  # e.g. {"gte": ..., "lte": ...}
            range_kwargs = {}
            for k, v in value.items():
                if isinstance(v, str):
                    try:
                        v = parse_iso8601_to_unix(v)
                    except ValueError:
                        continue  # skip invalid format
                range_kwargs[k] = v
            conditions.append(FieldCondition(key=key, range=Range(**range_kwargs)))
        elif value is not None:
            conditions.append(FieldCondition(key=key, match={"value": value}))

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
            metadata={
                k: v for k, v in vector_record.payload.items()
                if k not in {'chunk_id', 'data_input_source', 'ingestion_timestamp', 'content_timestamp'}
            }
        ) for vector_record in matching_vectors.points]
